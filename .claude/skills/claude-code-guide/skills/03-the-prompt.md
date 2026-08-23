---
name: the-prompt
description: Master the one prompt technique - Essential prompting strategies
keywords: ["prompting", "workflow", "productivity", "techniques"]
---

# The One Prompt You Need

Master the essential prompting technique for Claude Code.

## Core Concept

The "one prompt" approach focuses on clarity, context, and structure. One well-crafted prompt beats multiple fragmented ones.

## Prompt Structure

### 1. **Context Layer**
Start by providing context:
```
I'm working on [project type]
The goal is [specific objective]
Current status: [where you are]
```

### 2. **Task Definition**
Be specific about what you need:
```
I need to [action]
For [specific use case]
With these constraints: [limitations]
```

### 3. **Desired Output**
Clarify expected output:
```
Format: [desired format]
Length: [scope expectations]
Details: [level of detail needed]
```

## Examples

### Example 1: Code Review
```
Review this function for performance issues.
The function processes user data.
I'm concerned about O(n²) complexity.
Format: bullet points of issues with fixes.
```

### Example 2: Documentation
```
Write API documentation for our endpoints.
Target audience: frontend developers.
Include examples for each endpoint.
Format: Markdown with code blocks.
```

### Example 3: Architecture Discussion
```
Discuss database schema design for our user system.
Constraints: PostgreSQL, < 100ms queries.
Scale: 1M users expected in 2 years.
Format: diagrams and tradeoff analysis.
```

## Advanced Techniques

### Story-Based Organization
Organize prompts around user stories:
```
As a [user type]
I want to [action]
So that [outcome]
```

### Task Delegation
Break complex tasks:
1. **First question** - Ask the foundational question
2. **One at a time** - Get answers before proceeding
3. **Build on answers** - Use responses to inform next steps

### GitHub Integration
Reference issues and PRs:
```
Fix the issue described in #123
PR context: https://github.com/[owner]/[repo]/pull/[number]
```

## Notification Workflow

Use Notify to track:
- Long-running operations
- Complex analysis
- Multiple-step processes
- Team updates

## CEO/CTO Perspective

### For Leadership Decisions
```
I need analysis on [topic]
For executive decision-making
Budget/time constraints: [specifics]
Format: executive summary + detailed breakdown
```

### For Team Alignment
```
Document [feature/decision]
For team reference and onboarding
Include rationale and tradeoffs
Format: shared document ready for review
```

## Best Practices

✅ **Do:**
- Be specific and clear
- Provide relevant context
- State constraints upfront
- Clarify expected output
- Ask one clear question at a time

❌ **Don't:**
- Ask vague questions
- Omit important context
- Have unclear expectations
- Ask multiple unrelated things
- Change requirements mid-conversation

## Shortcuts & Tips

### Power Moves
- Reference previous conversations
- Use `/clear` to reset context if needed
- Leverage artifact tools for visual output
- Use Cowork for team collaboration

### Efficiency Patterns
- Keep prompts focused
- Reuse successful prompt structures
- Document what works
- Build prompt templates

## Integration with Tools

### With Artifact
```
Create a visual [component/diagram]
Based on [specifications]
Style: [design guidelines]
Interactive: [yes/no]
```

### With Cowork
```
Collaborate on [task]
Participants: [team members]
Share access to: [artifacts/documents]
```

### With Notifications
```
Execute [task]
Notify when: [specific condition]
Send notification to: [channel/method]
```

## Common Pitfalls

**❌ Too Vague:**
"Help me debug this"
**✅ Better:**
"Debug this authentication error - logs show 401 at login endpoint, expected 200"

**❌ Too Long:**
"I have this big project and I need everything done..."
**✅ Better:**
"Start with the database schema for [feature]"

**❌ Unclear Goal:**
"Make this better"
**✅ Better:**
"Optimize this query for sub-100ms response time"

## Next Steps

1. Practice with sample projects
2. Build your own prompt templates
3. Track what works best
4. Share effective prompts with team

---

**Difficulty:** Intermediate
**Time to Master:** 30 minutes practice
**Impact:** 10x productivity improvement
