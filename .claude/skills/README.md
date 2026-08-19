# 9 Claude Skills for Better Prompt Engineering

These are 9 reusable skills designed to help you write better prompts, optimize for specific Claude models, and create professional outputs. Use them individually or chain them together for maximum effectiveness.

## The Skills Pipeline

```
START: Messy Idea
        ↓
    1. Prompt Maker (/prompt-master)
       "Brain dump in, clean task spec out"
        ↓
    2. Grill Me (/grill-me)
       "Ask questions until nothing is vague"
        ↓
    3. How To (/how-to)
       "Map the steps you don't know yet"
        ↓
    ┌─────────────────┬──────────────────────────┐
    ↓                 ↓                          ↓
 4. Optimizer      5. Anti-AI              6. Personal Voice
    (/48)             (/anti-ai)            (/personal-voice)
 "For Opus 4.8"    "Remove AI tells"      "Sound like you"
    ↓                 ↓                      ↓
    └─────────────────┴──────────────────────────┘
                      ↓
         7. Fable Prompter (/fable)
         "Optimize for Fable 5"
                      ↓
         8. Write a Skill (/write-a-skill)
         "Bottle as reusable skill"
                      ↓
         9. Hand Off (/handoff)
         "Create handoff doc for next chat"
                      ↓
              FINISH: Ready to Use
```

## Quick Reference

### When to Use Each Skill

| Skill | Use When | Input | Output |
|-------|----------|-------|--------|
| Prompt Maker | Your idea is vague/messy | Rough concept | Clear task spec |
| Grill Me | You need to eliminate ambiguity | Existing prompt | Questions + clarifications |
| How To | You need step-by-step guidance | A goal/task | Detailed instructions |
| Optimizer 4.8 | Using Claude Opus 4.8 | Your draft prompt | Optimized prompt |
| Anti-AI | Your output sounds too robotic | Draft text | Natural-sounding version |
| Personal Voice | Want it to match your style | Draft + voice samples | Rewritten in your voice |
| Fable Prompter | Using Claude Fable 5 | Your draft prompt | Fable-optimized prompt |
| Write a Skill | You repeat a workflow constantly | Your workflow description | Reusable skill documentation |
| Hand Off | Ending a session/project | Your work summary | Handoff document |

## How to Use These Skills

### Option 1: Use Directly
Each skill file contains a complete prompt you can copy and use immediately. Just open the file and follow the "Start with" instruction.

### Option 2: Reference in Conversations
In Claude, you can reference these by describing what you need:
- "Use your Prompt Maker skill..."
- "Apply the Anti-AI skill to my draft..."
- "Create a handoff doc..."

### Option 3: Chain Skills Together
For best results on complex tasks, use multiple skills in sequence:

```
messy idea → prompt-maker → grill-me → how-to → optimizer → anti-ai → personal-voice
```

## Example Workflows

### Workflow 1: Create a Professional Blog Post
```
1. Prompt Maker: Turn your rough idea into clear spec
2. How To: Map the structure/steps
3. Grill Me: Ensure clarity on audience, tone, length
4. Anti-AI: Make it sound natural
5. Personal Voice: Match your blog's style
→ Ready to publish!
```

### Workflow 2: Build a New Reusable Skill
```
1. Prompt Maker: Clarify what the skill does
2. Grill Me: Get all the details right
3. Write a Skill: Package it properly
4. Optimizer: Polish the prompt
→ Ready to share or use repeatedly!
```

### Workflow 3: Optimize for Specific Model
```
1. Your prompt + requirements
2. (If Opus): Optimizer 4.8
3. (If Fable): Fable Prompter
4. Anti-AI: Natural voice
→ Optimized for your chosen model!
```

### Workflow 4: End-of-Session Documentation
```
1. Summarize your work session
2. Hand Off: Create comprehensive handoff doc
→ Ready for next session/handoff to colleague!
```

## Tips for Best Results

- **Prompt Maker:** Start here if you're not sure what you want
- **Grill Me:** Never skip this if clarity matters
- **How To:** Great for learning or teaching others
- **Optimizer/Fable:** Pick based on which model you're using
- **Anti-AI:** Always useful for final polish
- **Personal Voice:** Provide multiple writing samples for better results
- **Write a Skill:** Best for workflows you use 3+ times
- **Hand Off:** Do this BEFORE ending a session with unfinished work

## File Structure

```
.claude/
└── skills/
    ├── 01-prompt-maker.md
    ├── 02-grill-me.md
    ├── 03-how-to.md
    ├── 04-optimizer-opus.md
    ├── 05-anti-ai.md
    ├── 06-personal-voice.md
    ├── 07-fable-prompter.md
    ├── 08-write-a-skill.md
    ├── 09-hand-off.md
    └── README.md (this file)
```

## Getting Started

1. **Pick a skill** from the list above
2. **Open the corresponding file** from `.claude/skills/`
3. **Follow the "⚡ Start with" instruction**
4. **Provide your input** - the skill will guide you
5. **Get results** - use the output to improve your work

## Questions?

Each skill file includes:
- Purpose statement
- How to use instructions  
- Full prompt details
- Example inputs and outputs
- Activation instructions

Start with the skill that matches your current need!

---

**Made for:** Better prompt engineering, clearer thinking, and more effective Claude usage

**Created:** August 2026

**Attribution:** Inspired by "9 Claude Skills that write your prompts for you" - a framework for progressive prompt refinement
