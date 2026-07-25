# 03 — System Architecture

## High-Level Architecture

```
                          ┌─────────────────┐
                          │   Load Balancer  │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
          ┌─────────▼────┐  ┌─────▼──────┐  ┌───▼──────────┐
          │  Next.js      │  │  NestJS    │  │  FastAPI      │
          │  (Frontend)   │  │  (Gateway) │  │  (AI Backend) │
          └───────┬───────┘  └─────┬──────┘  └───┬──────────┘
                  │                │              │
                  └────────────────┼──────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
          ┌─────────▼────┐  ┌─────▼──────┐  ┌───▼──────────┐
          │  PostgreSQL   │  │   Redis    │  │  Celery      │
          │  + pgvector   │  │            │  │  Workers     │
          └───────────────┘  └────────────┘  └──────────────┘
```

## Service Boundaries

### Frontend (Next.js — Port 3000)

**Responsibilities:**
- Render UI with Tailwind + shadcn/ui
- Client-side state management with Zustand
- API data fetching with React Query
- Real-time updates via Socket.IO client
- Authentication state management

**Does NOT:**
- Direct AI model access
- Direct database queries
- Business logic

### API Gateway (NestJS — Port 3001)

**Responsibilities:**
- Authentication & authorization (JWT validation, RBAC, ACL)
- Request routing to AI Backend
- WebSocket gateway for real-time events
- Rate limiting and throttling
- Request/response validation and transformation
- Audit logging middleware

**Does NOT:**
- AI model execution
- Document processing
- Vector search

### AI Backend (FastAPI — Port 8000)

**Responsibilities:**
- RAG pipeline (ingestion, chunking, embedding, retrieval)
- Agent execution (LangGraph, tool calling)
- MCP Client/Server implementation
- LLM integration and serving
- Evaluation and metrics

**Does NOT:**
- Authentication (validates tokens only)
- User management
- Session management

### Celery Workers

**Responsibilities:**
- Document ingestion and processing
- Embedding generation (batch)
- Scheduled knowledge base syncs
- Evaluation runs
- Report generation

### PostgreSQL + pgvector

**Responsibilities:**
- User data and profiles
- RBAC roles and permissions
- Knowledge base metadata
- Document chunks with vector embeddings
- Audit logs

### Redis

**Responsibilities:**
- Session cache
- Rate limiting counters
- Celery message broker
- Real-time pub/sub
- Short-lived result cache

## Data Flow

### RAG Query Flow

```
User Query → Gateway → AI Backend
                          │
                    ┌─────▼─────┐
                    │  Embedding │
                    │  Generation│
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │  Vector    │
                    │  Search    │ ← pgvector
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │  LLM       │
                    │  Generation│
                    └─────┬─────┘
                          │
User ← Gateway ← Response + Citations
```

### Agent Execution Flow

```
User Task → Gateway → AI Backend
                          │
                    ┌─────▼─────┐
                    │  LangGraph │
                    │  Planner   │
                    └─────┬─────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
        ┌─────▼────┐ ┌───▼────┐ ┌───▼────────┐
        │  Tool A  │ │ Tool B │ │  Reasoning  │
        └─────┬────┘ └───┬────┘ └───┬────────┘
              │           │           │
              └───────────┼───────────┘
                          │
                    ┌─────▼─────┐
                    │  Final     │
                    │  Response  │
                    └───────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────┐
│                   TLS 1.3                    │
├─────────────────────────────────────────────┤
│  JWT Authentication (Access + Refresh)       │
├─────────────────────────────────────────────┤
│  RBAC (Role-Based Access Control)            │
├─────────────────────────────────────────────┤
│  ACL (Resource-Level Permissions)            │
├─────────────────────────────────────────────┤
│  Input Validation & Sanitization             │
├─────────────────────────────────────────────┤
│  Rate Limiting                               │
├─────────────────────────────────────────────┤
│  Audit Logging                               │
└─────────────────────────────────────────────┘
```
