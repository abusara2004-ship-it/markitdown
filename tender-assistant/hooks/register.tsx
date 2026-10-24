import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { SavedNote } from '../types'

const PANE = 'tender-status'
const NOTES_FILE = 'tender-notes.json'

// Change a tag when the value's shape changes: an earlier version's value is
// then declined instead of misread.
const client = atom({ plugin: 'tender-assistant', key: 'client' } as const, '', {
  shape: 'client-1',
})
const tender = atom({ plugin: 'tender-assistant', key: 'tender' } as const, '', {
  shape: 'tender-1',
})
const calls = atom({ plugin: 'tender-assistant', key: 'calls' } as const, 0, {
  shape: 'calls-1',
})
const lastNote = atom(
  { plugin: 'tender-assistant', key: 'lastNote' } as const,
  null as SavedNote | null,
  { shape: 'last-note-1' },
)

// ---------------------------------------------------------------- arguments

type Field = { key: string; label: string; aliases: string[] }

const CHECK_FIELDS: Field[] = [
  { key: 'client', label: 'Client name', aliases: ['client'] },
  { key: 'rfq', label: 'Tender / RFQ number', aliases: ['rfq', 'tender', 'number'] },
  { key: 'scope', label: 'Scope of supply', aliases: ['scope'] },
  { key: 'delivery', label: 'Delivery terms', aliases: ['delivery', 'incoterms'] },
  { key: 'warranty', label: 'Warranty period', aliases: ['warranty'] },
  { key: 'certs', label: 'Required certifications', aliases: ['certs', 'certifications'] },
  { key: 'exclusions', label: 'Exclusions', aliases: ['exclusions', 'excl'] },
  { key: 'validity', label: 'Commercial validity', aliases: ['validity', 'valid'] },
]

const NOTE_FIELDS: Field[] = [
  { key: 'supplier', label: 'Supplier / OEM name', aliases: ['supplier', 'oem'] },
  { key: 'product', label: 'Product or package', aliases: ['product', 'package'] },
  { key: 'certs', label: 'Certifications', aliases: ['certs', 'certifications'] },
  { key: 'lead', label: 'Lead time', aliases: ['lead', 'leadtime'] },
  { key: 'price', label: 'Price basis', aliases: ['price', 'pricebasis'] },
  { key: 'notes', label: 'Notes', aliases: ['notes', 'note'] },
]

// "key=value | key=value": a value may hold commas, never a pipe.
const parseArgs = (args: string, fields: Field[]): Record<string, string> => {
  const out: Record<string, string> = {}
  for (const part of args.split('|')) {
    const at = part.indexOf('=')
    if (at < 1) continue
    const name = part.slice(0, at).trim().toLowerCase().replace(/[\s_-]/g, '')
    const field = fields.find(f => f.aliases.includes(name))
    if (field) out[field.key] = part.slice(at + 1).trim()
  }
  return out
}

const SKIP = 'Not specified'

// Fills what the arguments left out. Free text goes under the dialog's "Other".
const collect = async (
  $: { ui: { ask: (q: string, o?: readonly string[]) => Promise<string> } },
  fields: Field[],
  given: Record<string, string>,
): Promise<Record<string, string> | undefined> => {
  const out = { ...given }
  for (const f of fields) {
    if (out[f.key] !== undefined) continue
    try {
      const answer = (await $.ui.ask(`${f.label}? (choose "Other" to type it)`, [SKIP, 'TBC'])).trim()
      out[f.key] = answer === SKIP ? '' : answer
    } catch {
      return undefined
    }
  }
  return out
}

// ------------------------------------------------------------ project files

type Doc = { path: string; text: string }

const SKIP_DIRS = new Set(['.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'])
const TEXT_EXT = /\.(md|txt|csv|json|ya?ml|html?|rst|tex|xml|log)$/i
const MAX_FILES = 400
const MAX_DEPTH = 3

type Fs = {
  list: (p?: string) => Promise<{ name: string; kind: 'file' | 'dir' | 'other'; size: number }[]>
  read: (p: string) => Promise<string>
}

const scan = async ($: { fs: Fs }): Promise<{ names: string[]; docs: Doc[] }> => {
  const names: string[] = []
  const docs: Doc[] = []
  const walk = async (dir: string, depth: number): Promise<void> => {
    if (names.length >= MAX_FILES) return
    const entries = await $.fs.list(dir === '' ? undefined : dir).catch(() => [])
    for (const e of entries) {
      const path = dir === '' ? e.name : `${dir}/${e.name}`
      if (e.kind === 'dir') {
        if (depth < MAX_DEPTH && !SKIP_DIRS.has(e.name)) await walk(path, depth + 1)
      } else if (e.kind === 'file' && names.length < MAX_FILES) {
        names.push(path)
        // The notes file is this mod's own output: not evidence for a tender.
        if (TEXT_EXT.test(e.name) && e.name !== NOTES_FILE && e.size <= 200_000) {
          const text = await $.fs.read(path).catch(() => '')
          docs.push({ path, text: text.toLowerCase() })
        }
      }
    }
  }
  await walk('', 0)
  return { names, docs }
}

const norm = (s: string) => s.toLowerCase().replace(/[\s_-]+/g, ' ').trim()

const findIn = (docs: Doc[], names: string[], needle: string | RegExp): string | undefined => {
  const hit = (s: string) =>
    typeof needle === 'string' ? norm(s).includes(norm(needle)) : needle.test(s)
  return (
    docs.find(d => hit(d.text) || hit(d.path))?.path ?? names.find(n => hit(n))
  )
}

// ------------------------------------------------------------- /tender-check

type Row = { item: string; state: 'present' | 'input-only' | 'missing'; where?: string }

const buildCheck = (v: Record<string, string>, docs: Doc[], names: string[]): Row[] => {
  const rows: Row[] = []
  const add = (item: string, given: boolean, evidence?: string) =>
    rows.push({
      item,
      state: evidence !== undefined ? 'present' : given ? 'input-only' : 'missing',
      where: evidence,
    })

  add(`Client: ${v.client || '—'}`, !!v.client, v.client ? findIn(docs, names, v.client) : undefined)
  add(`RFQ/tender no: ${v.rfq || '—'}`, !!v.rfq, v.rfq ? findIn(docs, names, v.rfq) : undefined)
  add(
    `Scope of supply${v.scope ? `: ${v.scope}` : ''}`,
    !!v.scope,
    findIn(docs, names, /scope of supply|bill of (quantities|materials)|\bboq\b|\bbom\b|scope/),
  )
  add(
    `Delivery terms${v.delivery ? `: ${v.delivery}` : ''}`,
    !!v.delivery,
    findIn(docs, names, /incoterm|\b(exw|fca|fob|cif|cfr|dap|ddp)\b|delivery (terms|schedule|time)/),
  )
  add(
    `Warranty${v.warranty ? `: ${v.warranty}` : ''}`,
    !!v.warranty,
    findIn(docs, names, /warrant/),
  )
  const certs = (v.certs ?? '').split(/[,;/]+/).map(s => s.trim()).filter(Boolean)
  if (certs.length === 0) add('Required certifications', false)
  for (const c of certs) add(`Certification: ${c}`, true, findIn(docs, names, c))
  add(
    `Exclusions${v.exclusions ? `: ${v.exclusions}` : ''}`,
    !!v.exclusions,
    findIn(docs, names, /exclusion|excluded|not included/),
  )
  add(
    `Commercial validity${v.validity ? `: ${v.validity}` : ''}`,
    !!v.validity,
    findIn(docs, names, /validity|valid for|valid until/),
  )

  // Documents a tender pack normally carries, whether or not the user listed them.
  const extras: [string, RegExp][] = [
    ['Technical datasheet / specification', /datasheet|data sheet|technical (spec|offer|proposal)/],
    ['Price schedule / commercial offer', /price (schedule|list|sheet)|commercial (offer|proposal)|quotation|quote/],
    ['Compliance matrix / deviation list', /compliance (matrix|statement)|deviation/],
    ['OEM / principal authorization letter', /authori[sz]ation (letter|certificate)|authori[sz]ed (dealer|distributor|agent)|principal/],
    ['ICV / local content plan', /\bicv\b|in[- ]country value|local content/],
    ['HSE / QA-QC documentation', /\bhse\b|\bqa\/?qc\b|quality (plan|manual)|iso 9001/],
  ]
  for (const [label, re] of extras) {
    const where = findIn(docs, names, re)
    rows.push({ item: label, state: where ? 'present' : 'missing', where })
  }
  return rows
}

const renderCheck = (v: Record<string, string>, rows: Row[], fileCount: number, docCount: number): string => {
  const present = rows.filter(r => r.state === 'present')
  const inputOnly = rows.filter(r => r.state === 'input-only')
  const missing = rows.filter(r => r.state === 'missing')
  const lines: string[] = []
  lines.push(`TENDER CHECK — ${v.client || 'client TBC'} / ${v.rfq || 'RFQ TBC'}`)
  lines.push(`Scanned ${docCount} text files of ${fileCount} found (PDF/Word/Excel are matched by file name only).`)
  lines.push('')
  lines.push(`ITEMS PRESENT (${present.length})`)
  for (const r of present) lines.push(`  [x] ${r.item}  <- ${r.where}`)
  if (present.length === 0) lines.push('  (none)')
  lines.push('')
  lines.push(`GIVEN BUT NOT FOUND IN PROJECT FILES (${inputOnly.length})`)
  for (const r of inputOnly) lines.push(`  [~] ${r.item}`)
  if (inputOnly.length === 0) lines.push('  (none)')
  lines.push('')
  lines.push(`ITEMS MISSING (${missing.length})`)
  for (const r of missing) lines.push(`  [ ] ${r.item}`)
  if (missing.length === 0) lines.push('  (none)')
  lines.push('')
  lines.push('RECOMMENDED NEXT ACTIONS')
  const actions: string[] = []
  if (inputOnly.length) actions.push(`Put the "[~]" terms into the offer documents so they are on record (${inputOnly.length} item${inputOnly.length > 1 ? 's' : ''}).`)
  for (const r of missing.slice(0, 6)) actions.push(`Add or obtain: ${r.item}.`)
  if (missing.length > 6) actions.push(`...and ${missing.length - 6} more missing items above.`)
  if (actions.length === 0) actions.push('Nothing outstanding in the files scanned. Do a final read against the RFQ itself.')
  actions.forEach((a, i) => lines.push(`  ${i + 1}. ${a}`))
  lines.push('')
  lines.push('Keyword match only: confirm each item against the RFQ text before submission.')
  return lines.join('\n')
}

// ------------------------------------------------------------- /tender-note

type Note = Record<string, string>

const loadNotes = async ($: { fs: Fs & { exists: (p: string) => Promise<boolean> } }): Promise<Note[]> => {
  if (!(await $.fs.exists(NOTES_FILE))) return []
  const raw = await $.fs.read(NOTES_FILE)
  const parsed: unknown = JSON.parse(raw)
  const list = (parsed as { notes?: unknown })?.notes
  if (!Array.isArray(list)) throw new Error(`${NOTES_FILE} has no "notes" array`)
  return list as Note[]
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'tender-check',
      description: 'Compliance checklist for a tender/RFQ against the project files',
      argumentHint: '[client=.. | rfq=.. | scope=.. | delivery=.. | warranty=.. | certs=.. | exclusions=.. | validity=..]',
    })
    await $.command.register({
      name: 'tender-note',
      description: `Save a supplier/OEM technical note to ${NOTES_FILE}`,
      argumentHint: '[supplier=.. | product=.. | certs=.. | lead=.. | price=.. | notes=..]',
    })
    await $.command.register({
      name: 'tender-status',
      description: 'Open the tender status pane',
    })

    // Show the last note already on disk, if any.
    try {
      const notes = await loadNotes($)
      const last = notes[notes.length - 1]
      if (last) {
        await update($, lastNote, () => ({
          supplier: last.supplier ?? '',
          product: last.product ?? '',
          savedAt: last.savedAt ?? '',
        }))
      }
    } catch {
      // A damaged notes file is reported when a note is saved, not at start.
    }

    void $.ui.open({ id: PANE, title: 'Tender status' })
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    await update($, calls, n => n + 1)
    return next(e)
  }).catch(($, e, next) => next(e))

  on('command.run', { command: 'tender-status' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Tender status' })
    return { text: 'Tender status pane opened.' }
  })

  on('command.run', { command: 'tender-check' }, async ($, e) => {
    const given = parseArgs(e.args, CHECK_FIELDS)
    const v = await collect($, CHECK_FIELDS, given)
    if (!v) return { text: 'Tender check cancelled.' }

    await update($, client, () => v.client ?? '')
    await update($, tender, () => v.rfq ?? '')

    const { names, docs } = await scan($)
    const rows = buildCheck(v, docs, names)
    return { text: renderCheck(v, rows, names.length, docs.length) }
  })

  on('command.run', { command: 'tender-note' }, async ($, e) => {
    const given = parseArgs(e.args, NOTE_FIELDS)
    const v = await collect($, NOTE_FIELDS, given)
    if (!v) return { text: 'Tender note cancelled.' }
    if (!v.supplier) return { text: 'Not saved: a supplier/OEM name is required.' }

    let notes: Note[]
    try {
      notes = await loadNotes($)
    } catch (err) {
      return {
        text: `Not saved: ${NOTES_FILE} could not be read (${(err as Error).message}). Fix or move it, then retry.`,
      }
    }

    const savedAt = new Date().toISOString()
    notes.push({
      savedAt,
      client: await read($, client),
      tender: await read($, tender),
      supplier: v.supplier,
      product: v.product ?? '',
      certifications: v.certs ?? '',
      leadTime: v.lead ?? '',
      priceBasis: v.price ?? '',
      notes: v.notes ?? '',
    })
    await $.fs.write(NOTES_FILE, JSON.stringify({ notes }, null, 2) + '\n')
    await update($, lastNote, () => ({ supplier: v.supplier!, product: v.product ?? '', savedAt }))

    return { text: `Saved note #${notes.length} for ${v.supplier} to ${NOTES_FILE}.` }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const c = await read($, client)
    const t = await read($, tender)
    const n = await read($, calls)
    const note = await read($, lastNote)

    return (
      <Box flexDirection="column">
        <Text>Client: {c || '(run /tender-check)'}</Text>
        <Text>Tender: {t || '(none)'}</Text>
        <Text>Tool calls: {String(n)}</Text>
        <Text>
          Last note: {note ? `${note.supplier}${note.product ? ` / ${note.product}` : ''}` : '(none yet)'}
        </Text>
        {note && <Text dimColor>saved {note.savedAt}</Text>}
      </Box>
    )
  })
}
