import { expect, test } from 'claude-code/testing'

const PANE = {
  plugin: 'tender-assistant',
  component: 'Pane',
  requestId: 'tender-status',
  props: {
    title: 'Tender status',
    isFocused: false,
    bodyColumns: 40,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 20 },
    view: {},
  },
} as const

const files: Record<string, string> = {
  'offer.md': 'Quotation RFQ-1234 for PDO. Delivery: DAP Sohar. Warranty 24 months. ATEX certified.',
}
let written: Record<string, string> = {}

const base = (p: string) => p.slice(p.lastIndexOf('/') + 1)

const engine = ($: any, on: any) => {
  on('command.register', () => ({ value: { command: 'x' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: any, e: any) => ({ cwd: e.cwd }))
  on('fs.exists', (_: any, e: any) => ({ value: base(e.path) in written }))
  on('fs.list', () => ({
    value: Object.keys(files).map(name => ({ name, kind: 'file', size: 10, mtimeMs: 0, isLink: false })),
  }))
  on('fs.read', (_: any, e: any) => ({ value: written[base(e.path)] ?? files[base(e.path)] ?? '' }))
  on('fs.write', (_: any, e: any) => {
    written[base(e.path)] = e.text
    return { value: undefined }
  })
}

test('tender-check lists present, input-only and missing items', async ($, on) => {
  engine($, on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const r = await $.command.run({
    command: 'tender-check',
    args: 'client=PDO | rfq=RFQ-1234 | scope=Pumps | delivery=DAP | warranty=24 months | certs=ATEX, IECEx | exclusions=Civil works | validity=90 days',
  })
  expect(r.text).toContain('[x] RFQ/tender no: RFQ-1234')
  expect(r.text).toContain('[x] Certification: ATEX')
  expect(r.text).toContain('[~] Certification: IECEx')
  expect(r.text).toContain('[ ] OEM / principal authorization letter')
})

test('tender-note saves to tender-notes.json and the pane shows it', async ($, on) => {
  engine($, on)
  written = {}
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const r = await $.command.run({
    command: 'tender-note',
    args: 'supplier=Acme | product=Skid pump | certs=ATEX | lead=14 weeks | price=EXW USD | notes=ok',
  })
  expect(r.text).toContain('Saved note #1')
  expect(JSON.parse(written['tender-notes.json']).notes[0].supplier).toBe('Acme')

  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ type: 'Text', text: /Last note/ }))?.text).toContain('Acme / Skid pump')
  await ui.unmount()
})
