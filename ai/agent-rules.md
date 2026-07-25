# Agent Rules

## Agent Execution Rules

### 1. Planning

- Always create a plan before executing multi-step tasks
- Break complex tasks into manageable, sequential steps
- Identify dependencies between steps
- Consider failure modes for each step

### 2. Tool Selection

- Choose the most appropriate tool for each subtask
- Prefer simpler tools over complex ones when both suffice
- Validate tool inputs against schemas before calling
- Never call a tool without understanding its purpose

### 3. Execution

- Execute steps in planned order
- Handle tool errors gracefully with retries or fallbacks
- Share intermediate results with the user when relevant
- Respect rate limits and timeouts

### 4. Self-Correction

- If a step fails, analyze why before retrying
- Adjust the plan if new information emerges
- Don't loop infinitely — set a max iteration limit (default: 10)
- If stuck, explain the situation to the user and ask for guidance

### 5. Completion

- Verify the task was completed successfully
- Summarize what was accomplished
- Note any limitations or caveats
- Ask if the user needs anything else

## Agent State Machine

```
START → PLAN → EXECUTE → EVALUATE → COMPLETE
                ↑            │
                └── RETRY ←──┘ (if failed & retries < max)
                              │
                              └── FAIL (if retries exhausted)
```

## Safety Rules

1. **No destructive actions** without explicit user confirmation
2. **No data exfiltration** — don't send internal data to external services
3. **No privilege escalation** — operate within granted permissions only
4. **Rate limit awareness** — don't hammer APIs
5. **Timeout handling** — respect max execution time

## Error Handling Protocol

```
  Tool Call
      │
      ▼
  Success? ──Yes──→ Continue
      │
      No
      │
      ▼
  Retryable? ──Yes──→ Retry (max 3, exponential backoff)
      │
      No
      │
      ▼
  Fallback available? ──Yes──→ Use fallback
      │
      No
      │
      ▼
  Report error to user, suggest alternatives
```

## Memory Management

- Keep conversation context within token limits
- Summarize older messages when approaching limits
- Store important facts for the duration of the session
- Don't retain sensitive information after task completion
