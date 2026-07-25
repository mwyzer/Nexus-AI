# Phase 03 — Agent System

## Goal

Build the autonomous agent runtime using LangGraph with tool calling, conversation memory, multi-step reasoning, and real-time step visualization.

## Prerequisites

- Phase 01 (Foundation) complete
- Phase 02 (RAG) complete (agents use RAG as a tool)

## Tasks

### 3.1 — Agent Runtime (LangGraph)
- [ ] Implement AgentState type definition
- [ ] Build Plan → Execute → Evaluate → Synthesize graph
- [ ] Implement conditional routing in graph
- [ ] Add max iterations and timeout safeguards
- [ ] Implement agent cancellation
- [ ] Add streaming support for agent steps

### 3.2 — Tool Calling Framework
- [ ] Create base Tool class with schema validation
- [ ] Implement ToolRegistry for tool management
- [ ] Create built-in tools:
  - [ ] Knowledge base search tool
  - [ ] Calculator tool
  - [ ] Web search tool (optional)
  - [ ] Code executor tool (sandboxed)
- [ ] Implement tool result formatting
- [ ] Add tool call logging

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
- [ ] Unit tests for graph nodes
- [ ] Integration tests for agent execution
- [ ] Test tool calling with mock tools
- [ ] Test memory management
- [ ] Test error recovery
- [ ] Test cancellation

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
