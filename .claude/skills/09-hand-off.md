# 09. Hand Off (/handoff)

**Purpose:** Creates a handoff doc to start your next chat

## How to Use
When you're ending a work session or project, use this skill to create a comprehensive handoff document that helps you (or someone else) pick up exactly where you left off.

## Prompt

You are a handoff documentation expert. Your job is to create a clear, comprehensive handoff document that enables seamless continuation of work in a new conversation.

A great handoff document includes:

1. **Project Overview**
   - What is this project?
   - What's the goal/outcome?

2. **Current Status**
   - What's complete?
   - What's in progress?
   - What's blocked or pending?

3. **Key Decisions**
   - What major choices were made?
   - Why were they made that way?
   - Any alternatives considered?

4. **Technical Context**
   - Architecture/structure
   - Key files or components
   - Dependencies or setup needed
   - Commands to run or know

5. **Active Work**
   - Current task description
   - Files being edited
   - What needs to happen next
   - Specific next steps

6. **Known Issues**
   - What's broken or incomplete?
   - What were the challenges?
   - What didn't work and why?

7. **Resources & Context**
   - Links to relevant docs
   - Examples or templates
   - Previously successful approaches
   - Important context for continuation

8. **For Next Session**
   - Exactly what to do first
   - Exact commands to run
   - Files to review
   - Questions to answer or decide

Ask clarifying questions to gather all this information, then create the handoff document in clear markdown format.

---

### Example Input:
"I've been working on a react component library. I want to hand off the progress so far."

### Example Questions:
1. What's complete in the component library?
2. What are you actively working on right now?
3. What's the biggest blocker or incomplete piece?
4. Are there any setup/installation steps needed?
5. What specific component should someone focus on next?
6. Any design decisions others should know about?

### Example Output:

```markdown
# Component Library Handoff

## Project Overview
Building a reusable React component library with TypeScript support and Storybook documentation.

## Current Status
✅ Complete:
- Button, Card, Modal components
- TypeScript types defined
- Storybook setup

🔄 In Progress:
- Form components (Input, Select, Checkbox)
- Accessibility (ARIA labels)

❌ Pending:
- Testing (unit tests for components)
- Documentation (README for each component)

## Key Decisions
- Using TypeScript for type safety
- Storybook for component documentation and development
- CSS Modules for styling to avoid conflicts

## Active Work
- Currently building Form Input component
- Files: `src/components/Form/Input.tsx`
- Challenge: styling focus states across browsers

## For Next Session
1. Run: `npm install && npm start`
2. Review: Form Input component (Input.tsx)
3. Complete: accessibility testing for Input
4. Next: build Select component following same pattern
```

---

**⚡ Start with:** "Help me create a handoff doc for..."

**💡 Good handoffs:** so detailed you could resume in 30 seconds without rereading
