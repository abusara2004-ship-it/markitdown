# 9 Claude Skills for Writing Better Prompts

Your personal prompt-writing workflow. These skills guide you from messy ideas to polished, reusable prompts.

## The Workflow

```
START: Messy Ideas
    ↓
FitMe → Clarify the vague problem
    ↓
PromptaMaker → Craft the prompt
    ↓
Optimizer → Polish & refine
    ↓
(Branch based on needs)
├─ Eventual Voice → Define your style
├─ Table Prompter → Structure outputs
└─ AuraAI → Refine tone
    ↓
WriteaSkill → Package as reusable skill
    ↓
HandOn → Create documentation
    ↓
FINISH: Ready to prompt!
```

---

## The 9 Skills

### 1. **FitMe** `/fitme`
**Clarify vague problems into specific ones**

When you have a half-baked idea but can't quite pin down what you need, FitMe asks clarifying questions to turn vagueness into specificity.

- Use when: Your problem feels fuzzy
- Output: Crystal-clear problem statement
- Next: Go to PromptaMaker

### 2. **PromptaMaker** `/promptamaker`
**Transform messy ideas into structured prompts**

Takes your rough thoughts and turns them into a real, working prompt with clear structure.

- Use when: You have an idea but not a prompt yet
- Output: A functional prompt draft
- Next: Go to Optimizer, or branch to Eventual Voice

### 3. **HowTo** `/howto`
**Map out step-by-step processes**

Turn "I don't know how to do X" into a complete walkthrough with prerequisites, steps, tips, and validation.

- Use when: You need a tutorial or walkthrough
- Output: Step-by-step guide
- Next: WriteaSkill or HandOn

### 4. **Optimizer** `/optimizer`
**Polish and refine existing prompts**

Takes a working prompt and makes it clearer, more efficient, and more reliable. Cuts down unnecessary words, clarifies ambiguity.

- Use when: Your prompt works but isn't perfect
- Output: A cleaner, more effective prompt
- Next: Branch to voice/tone skills or WriteaSkill

### 5. **Table Prompter** `/table-prompter`
**Create structured, table-based outputs**

For when you need organized, publishable data—spreadsheets, databases, structured lists.

- Use when: You need structured, comparable data
- Output: Prompt that generates clean table data
- Next: AuraAI for formatting, then WriteaSkill

### 6. **Eventual Voice** `/eventual-voice`
**Define your personal writing voice**

Codifies YOUR style so prompts sound like you, not generic AI. Creates a voice guide to embed in your prompts.

- Use when: You want consistency and personality
- Output: Voice guide + specifications
- Next: Apply to your prompts, then WriteaSkill

### 7. **AuraAI** `/auraai`
**Refine tone and style**

When your prompt works but sounds wrong—too formal, not witty enough, too technical. Adjusts tone without breaking function.

- Use when: Output tone isn't quite right
- Output: Revised prompt with right tone
- Next: Optimizer or WriteaSkill

### 8. **WriteaSkill** `/writeaskill`
**Package your prompt as a reusable skill**

Takes your refined prompt and turns it into a proper skill (.md file) you can use everywhere—Claude Chat, Cowork, Code.

- Use when: Your prompt is perfected and reusable
- Output: A production-ready skill file
- Next: Publish it, use it, or move to HandOn for docs

### 9. **HandOn** `/handon`
**Create comprehensive handbooks**

Full documentation for complex processes—tutorials, guides, case studies, troubleshooting. Everything someone needs to know.

- Use when: You want to teach or document deeply
- Output: Complete, shareable handbook
- Next: Share, train, iterate

---

## Quick Reference by Situation

### "I have a vague idea"
1. FitMe (clarify)
2. PromptaMaker (craft)
3. Optimizer (polish)

### "I need a walkthrough"
→ HowTo (create steps)

### "My prompt works but sounds wrong"
→ AuraAI (fix tone)

### "I want this as a reusable tool"
→ WriteaSkill (package it)

### "I need to teach someone"
→ HandOn (create handbook)

### "I need structured data"
→ Table Prompter (organize output)

### "I want everything to sound like me"
→ Eventual Voice (define your style)

---

## Using These Skills Across Platforms

✅ **Works in:** Claude Chat, Cowork, Claude Code
✅ **Invoke with:** `/skillname`
✅ **Share:** Add to any conversation, run in any workspace

---

## Pro Tips

- **Start messy** → FitMe first. Don't overthink it.
- **Iterate** → Come back to Optimizer and AuraAI multiple times
- **Document as you go** → Use HandOn once you have something good
- **Voice consistency** → Use Eventual Voice once, then refer to it always
- **Chain them** → Often you'll use 3-4 in sequence for a complex prompt
- **Personalize** → These are templates—adapt them to YOUR style

---

## File Structure

```
.claude/skills/
├── 01-promptamaker/SKILL.md
├── 02-fitme/SKILL.md
├── 03-howto/SKILL.md
├── 04-optimizer/SKILL.md
├── 05-table-prompter/SKILL.md
├── 06-eventual-voice/SKILL.md
├── 07-auraai/SKILL.md
├── 08-writeaskill/SKILL.md
└── 09-handon/SKILL.md
```

All skills are stored in your markitdown repository and ready to use.

---

**Start with FitMe or PromptaMaker depending on how clear your idea is. Then follow the flow.**

Happy prompting! 🚀
