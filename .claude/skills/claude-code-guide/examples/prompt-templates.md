# Claude Code Prompt Templates

Ready-to-use prompt templates for common scenarios.

## Table of Contents
1. [Code Review](#code-review)
2. [Architecture & Design](#architecture--design)
3. [Documentation](#documentation)
4. [Bug Fixes](#bug-fixes)
5. [Feature Development](#feature-development)
6. [Performance Optimization](#performance-optimization)
7. [Refactoring](#refactoring)

---

## Code Review

### Template 1: Security Review
```
Review this code for security vulnerabilities:
[paste code]

Focus areas:
- Input validation
- Authentication/authorization
- Data exposure risks
- Injection vulnerabilities
- Error handling

Format: Security concerns with severity + recommended fix
```

### Template 2: Performance Review
```
Analyze this code for performance issues:
[paste code]

Context:
- Data size: [scale]
- Frequency: [how often called]
- Performance target: [ms/operations]

Format: Issues ranked by impact with optimization suggestions
```

### Template 3: Readability Review
```
Make this code more readable:
[paste code]

Concerns:
- Complex logic
- Poor naming
- Missing comments
- Excessive nesting

Format: Refactored code with explanations of changes
```

---

## Architecture & Design

### Template 1: System Design
```
Design a system for [requirement]:
- Requirements: [specific needs]
- Scale: [expected growth]
- Tech stack: [current/preferred]
- Budget: [constraints]
- Timeline: [urgency]

Provide: Architecture diagram (text), tradeoff analysis, implementation roadmap
```

### Template 2: Database Schema
```
Design database schema for [feature]:
- Main entities: [list]
- Access patterns: [typical queries]
- Scale: [record count, growth]
- Performance target: [query time]
- Constraints: [GDPR, compliance, etc]

Provide: Schema diagram (SQL), relationship explanation, normalization reasoning
```

### Template 3: API Design
```
Design API for [feature]:
- Clients: [who will use it]
- Primary use cases: [key workflows]
- Performance needs: [latency, throughput]
- Auth requirements: [type needed]
- Scale: [expected requests/sec]

Provide: Endpoint specifications, error handling, version strategy
```

---

## Documentation

### Template 1: API Documentation
```
Generate API documentation for these endpoints:
[list endpoints with methods]

Format: 
- Description of what it does
- Request/response examples
- Error cases
- Rate limits
- Authentication required

Include: Code examples in [language]
```

### Template 2: Setup Guide
```
Create setup guide for [project]:
- Target audience: [beginners/experienced]
- Environment: [OS, tools needed]
- Time estimate: [how long setup should take]
- Common issues: [problems people face]

Format: Step-by-step with troubleshooting section
```

### Template 3: README
```
Write README for [project]:
- What it does: [purpose]
- Key features: [main selling points]
- Who should use it: [target users]
- Current maturity: [alpha/beta/stable]

Include sections:
- Quick start (5 minutes)
- Features
- Installation
- Usage examples
- Contributing
- License
```

---

## Bug Fixes

### Template 1: Debugging Help
```
Debug this issue:
- What happens: [describe behavior]
- Expected: [what should happen]
- Reproduces: [how to trigger it]
- Environment: [OS, versions, setup]
- Error logs: [paste relevant logs]
- Code context: [paste relevant code]

Help with: Root cause + solution approach
```

### Template 2: Browser Issue
```
Fix this browser issue:
- Symptom: [what users see]
- Browser: [Chrome/Firefox/Safari version]
- URL: [where it happens]
- Console errors: [paste errors]
- Relevant code: [paste HTML/CSS/JS]

Provide: Root cause + browser-specific solution
```

### Template 3: Performance Bug
```
Fix this performance issue:
- Metric: [load time/memory/CPU]
- Current: [actual numbers]
- Target: [acceptable numbers]
- Conditions: [when it's slow]
- Tools: [profiling data if available]

Provide: Bottleneck analysis + optimization strategy
```

---

## Feature Development

### Template 1: Feature Implementation
```
Implement [feature name]:
- User need: [why this feature matters]
- Acceptance criteria:
  1. [specific requirement]
  2. [specific requirement]
  3. [specific requirement]
- Constraints: [time, resources, dependencies]
- Dependencies: [other systems it connects to]

Approach: Design before code. Ask clarifying questions about tradeoffs.
```

### Template 2: Feature Breakdown
```
Break down this feature:
[describe feature]

Needed:
- UI mockups
- Data structure
- API contracts
- Edge cases
- Testing strategy
- Rollout plan

Provide: Phased implementation roadmap
```

### Template 3: Requirements Clarification
```
Help clarify requirements for [feature]:

Initial idea: [describe vaguely]
- Users: [who uses this]
- Problem it solves: [current pain point]
- Success metric: [how to measure success]

Ask me clarifying questions to refine requirements
```

---

## Performance Optimization

### Template 1: Query Optimization
```
Optimize this database query:
[paste query]

Context:
- Query frequency: [how often]
- Data size: [record count]
- Current time: [milliseconds]
- Target time: [desired milliseconds]
- Schema: [table structures]

Provide: Optimized query + explanation of improvements
```

### Template 2: Code Performance
```
Optimize this code:
[paste code]

Context:
- Runs: [frequency]
- Input size: [typical data volume]
- Current time: [if profiled]
- Target time: [desired time]
- Constraints: [memory, dependencies]

Provide: Optimized version + performance comparison
```

### Template 3: Frontend Performance
```
Improve frontend performance for [page/feature]:
- Current metrics: [LCP, FID, CLS, etc]
- Target metrics: [desired numbers]
- Traffic: [users/month]
- Device mix: [mobile vs desktop %%]
- Network: [typical speed]

Analyze: Core Web Vitals + improvement roadmap
```

---

## Refactoring

### Template 1: Code Cleanup
```
Refactor this code:
[paste code]

Goals:
- Readability: higher priority
- Performance: secondary
- Test coverage: maintain or improve
- Dependencies: don't add new ones

Constraints:
- Time: [available time]
- Risk tolerance: [low/medium/high]

Provide: Refactored code with migration path if breaking changes
```

### Template 2: Pattern Implementation
```
Refactor to use [design pattern]:
[paste current code]

Context:
- Why: [reason for refactoring]
- Pattern: [specific design pattern]
- Benefits: [what improvement you want]
- Constraints: [limitations]

Provide: Pattern implementation + explanation of benefits
```

### Template 3: Tech Upgrade
```
Upgrade from [old tech] to [new tech]:
[describe current implementation]

Migration scope:
- Modules affected: [list]
- User impact: [breaking changes?]
- Rollback plan: [how to revert?]
- Timeline: [urgency]

Strategy:
1. Parallel running
2. Feature flags
3. Big bang migration

Which approach and detailed steps?
```

---

## Meta Templates

### Template 1: "Teach Me"
```
Teach me about [topic] in context of Claude Code:
- My level: [beginner/intermediate/advanced]
- What I know: [prerequisites]
- What I want to apply: [goal]
- Time available: [learning time budget]

Format: Examples > Theory
```

### Template 2: "Design Review"
```
Review this design decision:
Context: [describe the situation]

Option A: [describe approach]
- Pros: [benefits]
- Cons: [drawbacks]

Option B: [describe approach]
- Pros: [benefits]
- Cons: [drawbacks]

What would you recommend and why?
```

### Template 3: "Workflow Discussion"
```
Help me improve this workflow:
Current approach: [describe how you work]
Pain points: [what's slow/annoying]
Constraints: [what can't change]

Suggest:
1. Quick wins (this week)
2. Medium improvements (this month)
3. Long-term changes (this quarter)
```

---

## Template Usage Tips

✅ **Customize for your context** - Don't use templates verbatim, adapt them
✅ **Be specific** - Replace [bracketed items] with actual details
✅ **Include constraints** - Tell Claude about limitations
✅ **Show your thinking** - Explain what you've tried already
✅ **Be clear about output** - Specify format you want

❌ **Don't** use generic templates
❌ **Don't** omit important context
❌ **Don't** ask vague follow-up questions
❌ **Don't** forget about constraints
❌ **Don't** change requirements mid-conversation

---

## Creating Your Own Templates

1. **Find what works** - Use templates that give good results
2. **Save successful prompts** - Build your own library
3. **Extract the pattern** - What made it work?
4. **Generalize it** - Make it reusable
5. **Document it** - Add to your team knowledge base

---

*Use these templates as starting points. The best prompts are customized to your specific context.*
