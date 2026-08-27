# Claude Skills Setup

Welcome! You now have **9 skills for writing better prompts** available across Claude Chat, Cowork, and Claude Code.

## Getting Started

### How to Use These Skills

#### In Claude Chat or Cowork
Type the skill name with a slash:
```
/fitme
/promptamaker
/optimizer
/eventual-voice
```

#### In Claude Code (Web or CLI)
```
/fitme - clarify your vague idea
/promptamaker - turn idea into prompt
/optimizer - polish your prompt
/eventual-voice - define your voice
/auraai - refine tone
/table-prompter - create structured output
/howto - create walkthrough
/writeaskill - package as reusable skill
/handon - create handbook
```

### The 9 Skills At a Glance

| # | Skill | Purpose | When to Use |
|---|-------|---------|-------------|
| 1 | **FitMe** | Clarify vague problems | "My idea is fuzzy" |
| 2 | **PromptaMaker** | Craft prompts from ideas | "I have an idea, no prompt" |
| 3 | **HowTo** | Create step-by-step guides | "I need a walkthrough" |
| 4 | **Optimizer** | Polish existing prompts | "It works but needs refinement" |
| 5 | **Table Prompter** | Structure data outputs | "I need organized data" |
| 6 | **Eventual Voice** | Define your writing style | "I want consistency" |
| 7 | **AuraAI** | Refine tone and personality | "The tone isn't right" |
| 8 | **WriteaSkill** | Package as reusable skill | "I want to reuse this everywhere" |
| 9 | **HandOn** | Create handbooks | "I need to document/teach" |

## Workflow Diagram

```
Messy Idea
    ↓
[FitMe] → Clarified Problem
    ↓
[PromptaMaker] → Draft Prompt
    ↓
[Optimizer] → Polished Prompt
    ↓
    ├─→ [Eventual Voice] → Styled Prompt
    ├─→ [AuraAI] → Tone-Adjusted Prompt  
    └─→ [Table Prompter] → Structured Prompt
    ↓
[WriteaSkill] → Reusable Skill
    ↓
[HandOn] → Complete Handbook
    ↓
READY TO USE! 🎉
```

## File Structure

```
.claude/
├── settings.json          ← Skill configuration
├── README.md             ← You are here
└── skills/
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

## Common Workflows

### Scenario 1: "I have a rough idea"
1. `/fitme` - Clarify what you really want
2. `/promptamaker` - Turn it into a prompt
3. `/optimizer` - Clean it up
4. `/writeaskill` - Make it reusable

### Scenario 2: "My prompt doesn't sound right"
1. `/optimizer` - Fix clarity
2. `/auraai` - Adjust tone
3. Check the output
4. `/writeaskill` - Save it

### Scenario 3: "I need to document a process"
1. `/howto` - Create the guide
2. `/optimizer` - Polish it
3. `/handon` - Turn it into a handbook

### Scenario 4: "I want consistency"
1. `/eventual-voice` - Define your voice once
2. Add to every future prompt (reference it in `/auraai`)

## Tips for Success

✅ **Start messy** - Don't overthink it, FitMe will help  
✅ **Iterate** - Come back to skills multiple times  
✅ **Personalize** - Adapt these to your style  
✅ **Share** - Use WriteaSkill to turn good prompts into team resources  
✅ **Document** - Use HandOn for complex processes  

## Where to Go Next

- **Learn the workflow**: See `CLAUDE.md` in the root directory
- **Quick reference**: Run `/fitme` or `/promptamaker` to get started
- **Full guide**: Explore each skill folder to see the complete SKILL.md

---

**Ready?** Start with `/fitme` if your idea is unclear, or `/promptamaker` if you already know what you want.

Happy prompting! 🚀
