# Phase 03 — Agent System

## Goal

Build the autonomous agent runtime using LangGraph with tool calling, conversation memory, multi-step reasoning, and real-time step visualization.

## Prerequisites

- Phase 01 (Foundation) complete
- Phase 02 (RAG) complete (agents use RAG as a tool)

## Tasks

### 3.1 — Agent Runtime (LangGraph)
- [x] Implement AgentState type definition — `app/agents/state.py`
- [x] Build Plan → Execute → Evaluate → Synthesize graph — `app/agents/graph.py` (no tool calling wired in yet, see 3.2)
- [x] Implement conditional routing in graph — `route_after_plan`/`route_after_evaluate` in `app/agents/nodes.py`
- [x] Add max iterations and timeout safeguards — `settings.agent_max_iterations`/`agent_timeout_seconds`, enforced in `app/agents/nodes.py` and `app/agents/runner.py`
- [x] Implement agent cancellation — `cancel_event` checked between steps in `app/agents/runner.py`
- [x] Add streaming support for agent steps — `stream_agent()` via `graph.astream()` in `app/agents/runner.py`

### 3.2 — Tool Calling Framework
- [x] Create base Tool class with schema validation — `app/agents/tools/base.py` (pydantic `args_schema`)
- [x] Implement ToolRegistry for tool management — `app/agents/tools/registry.py`
- [x] Create built-in tools:
  - [x] Knowledge base search tool — `app/agents/tools/knowledge_base.py` (wraps existing RAG hybrid search)
  - [x] Calculator tool — `app/agents/tools/calculator.py` (AST-based, no `eval()` — rejects anything non-arithmetic)
  - [ ] Web search tool (optional) — skipped, no search API/key configured
  - [ ] Code executor tool (sandboxed) — skipped, no sandbox infra exists; shipping an unsandboxed executor would be unsafe
- [x] Implement tool result formatting — consistent `[tool] result` / `[tool error] message` strings from `execute_node`
- [x] Add tool call logging — `ToolRegistry.execute()` logs name/args/duration/status

### 3.3 — Conversation Memory
- [ ] Implement BufferMemory (sliding window)
- [ ] Implement SummaryMemory (LLM summarization)
- [ ] Implement BufferSummaryMemory (hybrid)
- [ ] Add token counting and trimming
- [ ] Persist conversation history to database
- [ ] Load conversation history on resume

### 3.4 — Agent Types
- [ ] Implement RAG Agent (knowledge base Q&A)
- [ ] Implement Tool-Using Agent (multi-step tasks)
- [ ] Implement Chat Agent (conversational)
- [ ] Create agent configuration system
- [ ] Add agent templates

### 3.5 — Agent API
- [ ] Create agent CRUD endpoints
- [ ] Create agent run endpoint (sync)
- [ ] Create agent stream endpoint (SSE)
- [ ] Create agent status/cancel endpoints
- [ ] Create conversation management endpoints

### 3.6 — Gateway Integration
- [ ] **Gateway**: Agent CRUD endpoints
- [ ] **Gateway**: Conversation CRUD endpoints
- [ ] **Gateway**: Message endpoints
- [ ] Proxy agent run requests to AI Backend
- [ ] Stream agent steps via WebSocket

### 3.7 — Frontend
- [ ] Agent list page with cards
- [ ] Agent configuration page
- [ ] Agent chat interface
- [ ] Real-time step visualization component
- [ ] Conversation history sidebar
- [ ] Agent template gallery

### 3.8 — Testing
- [x] Unit tests for graph nodes — `tests/test_agent_graph.py`, `tests/test_agent_tools.py`
- [ ] Integration tests for agent execution — only exercised against a fake LLM so far, not a real provider
- [x] Test tool calling with mock tools — `tests/test_agent_tools.py` (directive parsing, registry, calculator, tool-error path)
- [ ] Test memory management — no memory exists yet (3.3)
- [ ] Test error recovery — no retry/recovery path exists yet if `complete()` raises mid-graph
- [x] Test cancellation — `tests/test_agent_graph.py::test_run_agent_raises_on_cancellation`

## Acceptance Criteria

- [ ] Agent can plan and execute multi-step tasks
- [ ] Agent correctly uses tools to gather information
- [ ] Agent recovers from tool errors
- [ ] Conversation memory persists across messages
- [ ] Real-time step visualization works in frontend
- [ ] Agent respects max iterations limit
- [ ] Agent can be cancelled mid-execution
- [ ] All tests pass

## Estimated Effort

5-7 days for a single developer.
