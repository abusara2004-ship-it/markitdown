export type SavedNote = {
  supplier: string
  product: string
  savedAt: string
}

declare module 'claude-code' {
  interface PluginState {
    'tender-assistant': {
      client: Shaped<string>
      tender: Shaped<string>
      calls: Shaped<number>
      lastNote: Shaped<SavedNote | null>
    }
  }
}
