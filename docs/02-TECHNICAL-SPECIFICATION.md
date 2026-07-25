# 02 — Technical Specification

## Technology Choices & Rationale

### Frontend: Next.js + TypeScript + Tailwind + shadcn/ui

| Choice         | Rationale                                         |
|----------------|---------------------------------------------------|
| Next.js 14+    | App Router, SSR/SSG, API routes, React Server Components |
| TypeScript     | Type safety, better DX, fewer runtime errors      |
| Tailwind CSS   | Utility-first, rapid prototyping, consistent design|
| shadcn/ui      | Accessible, customizable, copy-paste components   |

### API Gateway: NestJS + TypeScript + Socket.IO

| Choice         | Rationale                                         |
|----------------|---------------------------------------------------|
| NestJS         | Opinionated structure, DI, guards, interceptors   |
| Socket.IO      | Real-time bidirectional communication             |
| TypeScript     | Shared types with frontend                        |

### AI Backend: Python + FastAPI + Pydantic

| Choice         | Rationale                                         |
|----------------|---------------------------------------------------|
| FastAPI        | Async-native, auto-docs, high performance         |
| Pydantic v2    | Data validation, serialization, settings management|
| Python 3.11+   | Performance improvements, better asyncio          |

### AI Frameworks: LangChain + LangGraph

| Choice         | Rationale                                         |
|----------------|---------------------------------------------------|
| LangChain      | Rich ecosystem, document loaders, retrievers       |
| LangGraph      | Stateful agent orchestration, cyclic graphs       |

### RAG: PostgreSQL + pgvector

| Choice         | Rationale                                         |
|----------------|---------------------------------------------------|
| PostgreSQL     | Battle-tested, ACID compliant, existing infra     |
| pgvector       | Native vector search, HNSW index, hybrid search   |

### Background Jobs: Celery + Redis

| Choice         | Rationale                                         |
|----------------|---------------------------------------------------|
| Celery         | Robust task queue, scheduling, retries            |
| Redis          | Fast message broker and result backend            |

### MCP: MCP Client & Server

| Choice         | Rationale                                         |
|----------------|---------------------------------------------------|
| MCP Protocol   | Standardized AI-tool integration, growing ecosystem|

### Auth: JWT + RBAC + ACL

| Choice         | Rationale                                         |
|----------------|---------------------------------------------------|
| JWT            | Stateless, scalable, widely supported             |
| RBAC           | Role-based access control for coarse-grained auth |
| ACL            | Fine-grained resource-level permissions           |

### Infrastructure: Docker Compose

| Choice         | Rationale                                         |
|----------------|---------------------------------------------------|
| Docker Compose | Local dev parity, simple orchestration            |

## Development Standards

### TypeScript

- Strict mode enabled
- ESLint with recommended config
- Prettier for formatting
- Path aliases (`@/` for src)
- No `any` types without explicit justification

### Python

- Type hints on all public functions
- Pydantic models for all data structures
- Ruff for linting and formatting
- Pytest for testing
- Poetry for dependency management

### General

- Conventional commits
- PR reviews required
- CI runs lint + type-check + tests
- Environment variables for all config
- `.env.example` files committed, `.env` never
