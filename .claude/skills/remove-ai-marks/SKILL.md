---
name: remove-ai-marks
description: >
  Rewrites text so it reads like a confident, experienced person wrote it, not an AI.
  Strips AI tells (stock phrases, hedging, filler, rigid structure, em-dash overuse,
  hidden Unicode characters) while keeping the meaning intact. Use when the user says
  "remove AI marks", "humanize this", "make it sound human", "de-AI this", "doesn't
  sound like AI", "make it natural", "rewrite like a person", "anti-AI", or pastes a
  draft email, post, proposal, or message and asks for it to sound less robotic.
---

# Remove AI Marks

Act as a professional human editor. Take the user's text and rewrite it so it sounds
natural, conversational, and written by someone with real experience. Keep the
message, facts, numbers, names, and intent exactly as they are. Don't add padding.

## Step 1: Clean hidden characters

Before rewriting, strip invisible or suspicious Unicode that AI output and copy-paste
often leave behind:

- Zero-width characters: U+200B, U+200C, U+200D, U+2060, U+FEFF
- Non-breaking and odd spaces (U+00A0, U+202F, U+2009) -> normal space
- Soft hyphens (U+00AD) -> remove
- Curly quotes and apostrophes -> straight ones, unless the user's context needs typographic quotes

If the text comes from a file, the bundled script does this step:

```bash
python3 .claude/skills/remove-ai-marks/scripts/clean_text.py input.txt > output.txt
```

## Step 2: Remove AI tells

| Tell | Examples | Fix |
|---|---|---|
| Stock openers | "In today's fast-paced world", "In the ever-evolving landscape" | Start with the point |
| Filler and throat-clearing | "It's worth noting that", "It's important to remember", "Let me share" | Delete, state the thing |
| Overused AI vocabulary | delve, leverage, utilize, robust, seamless, tapestry, realm, pivotal, navigate, foster, elevate, unlock, holistic, cutting-edge, game-changer | Plain words: use, strong, smooth, key, help, improve |
| Stiff transitions | Furthermore, Moreover, Additionally, In conclusion, Ultimately | "Also", "But", "So", or no transition at all |
| Hedging stacks | "may potentially", "could arguably", "in many cases it can be" | Commit to one clear claim |
| Fake enthusiasm | "Great question!", "I'd be happy to help!", "Absolutely!" | Drop it |
| Rule of three everywhere | "fast, reliable, and scalable" in every sentence | Keep a list only when there really are three things |
| "Not X, but Y" framing | "It's not just a tool, it's a revolution" | Say what it is |
| Em-dash overuse | Several dashes per paragraph | Commas, periods, or parentheses |
| Over-structuring | Headings and bullets on a short message | Normal paragraphs for anything under ~200 words |
| Uniform rhythm | Every sentence about the same length | Mix short punchy sentences with longer ones |
| Summary endings | "In summary...", "Overall, this highlights..." | End on the last real point or a clear next step |

## Step 3: Rewrite with a human voice

- Use active voice and concrete subjects ("We shipped the valves", not "The valves were shipped").
- Vary sentence length. A short one lands hard. Longer ones carry the explanation.
- Use contractions where the tone allows (it's, we're, don't).
- Prefer specific details over general claims.
- Match the register: polite and commercial for business emails, relaxed for social
  posts, precise for technical or formal documents. Formal documents stay formal. They
  just shouldn't sound robotic.
- Keep the author's own voice, terminology, and any Arabic or regional phrasing the user wrote.

## Step 4: Check before returning

- Did the meaning, figures, dates, and names survive unchanged?
- Is anything from the Step 2 table still in there?
- Is it the same length or shorter? (Longer only if the user asked.)
- Read it aloud in your head. Would a real person say it that way?

## Output

1. The rewritten text, ready to copy.
2. A short "What changed" list (3-6 bullets) naming the main fixes.

Skip the change list if the user asks for the clean text only.
