# tender-assistant

A local helper for industrial OEM and oil & gas tender work. `/tender-check` asks for the tender terms (client, RFQ number, scope of supply, delivery, warranty, certifications, exclusions, validity) and compares them with the files in the current project, listing what is present, what is missing and what to do next. `/tender-note` saves supplier/OEM notes to `tender-notes.json` in the project folder. A status pane shows the active client, tender number, tool-call count and last saved note. `/tender-status` reopens the pane.

Everything stays on your machine: the mod only reads project files and writes `tender-notes.json`. It makes no network calls. Keep `tender-notes.json` out of version control if it holds pricing.

Arguments can be given inline as `key=value | key=value`, e.g. `/tender-check client=PDO | rfq=RFQ-1234 | certs=ATEX, ISO 9001`; anything left out is asked for.
