# Nexus AI

Enterprise AI Knowledge & Agent Platform — a modular, production-ready platform for building, deploying, and managing AI-powered knowledge bases, RAG pipelines, autonomous agents, and MCP tool integrations.

## Architecture Overview

### Business-Capability Architecture

```
                     NEXUS AI
                        │
      ┌─────────────────┼─────────────────┐
      │                 │                 │
      ▼                 ▼                 ▼
 AI Knowledge       AI Operations      AI Decisions
      │                 │                 │
      ▼                 ▼                 ▼
    RAG             Help Desk       Decision Manager
                        │                 │
                        └────────┬────────┘
                                 ▼
                            AI Agents
                                 │
                                 ▼
                               MCP
                                 │
                                 ▼
                      Enterprise Systems
```

### Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│                TypeScript · Tailwind · shadcn/ui             │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/WebSocket
┌───────────────────────────▼─────────────────────────────────┐
│                 API Gateway (NestJS)                         │
│           TypeScript · Socket.IO · JWT/RBAC/ACL              │
└──────────────┬────────────────────────────┬─────────────────┘
               │                            │
┌──────────────▼──────────┐  ┌──────────────▼─────────────────┐
│   AI Backend (FastAPI)   │  │   Background Jobs (Celery)     │
│  Python · LangChain      │  │   Python · Redis               │
│  LangGraph · Pydantic    │  │                                │
└──────────────┬───────────┘  └────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│              Data & Infrastructure                          │
│  PostgreSQL + pgvector · Redis · Docker Compose              │
│  MCP Client/Server · Local LLM Serving                      │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Layer            | Technology                              |
|------------------|------------------------------------------|
| Frontend         | Next.js, TypeScript, Tailwind, shadcn/ui |
| API Gateway      | NestJS, TypeScript, Socket.IO            |
| AI Backend       | Python, FastAPI, Pydantic                |
| AI Frameworks    | LangChain, LangGraph                     |
| RAG              | PostgreSQL + pgvector                    |
| Background Jobs  | Celery + Redis                           |
| MCP              | MCP Client & Server                      |
| Auth             | JWT + RBAC + ACL                         |
| Infrastructure   | Docker Compose                           |

## Development Principles

- **Modular architecture** — clear separation of concerns
- **Clean code** — readable, maintainable, well-documented
- **Type safety** — strict TypeScript & Pydantic models
- **Strong error handling** — graceful degradation everywhere
- **Testable components** — unit, integration, and e2e tests
- **Secure by default** — least privilege, secrets management
- **Production-ready patterns** — retry, circuit breaker, observability

## Project Structure

```
nexus-ai/
├── docs/          # Technical documentation & specifications
├── ai/            # AI system prompts, agent rules, RAG rules
├── tasks/         # Phase-by-phase implementation tasks
├── prompts/       # Development prompts for each layer
├── frontend/      # Next.js application
├── gateway/       # NestJS API Gateway
├── ai-backend/    # Python FastAPI AI services
├── infrastructure/# Docker Compose & deployment configs
└── scripts/       # Utility and setup scripts
```

## Getting Started

```bash
# Clone and enter the project
git clone <repo-url> nexus-ai && cd nexus-ai
cp .env.example .env  # then fill in real values

# Start all services (--env-file is required: docker-compose.yml lives in
# infrastructure/, so Compose's project directory defaults there, not repo root)
cd infrastructure && docker compose --env-file ../.env up -d --build

# Frontend
cd frontend && npm install && npm run dev

# API Gateway
cd gateway && npm install && npm run start:dev

# AI Backend
cd ai-backend && poetry install && poetry run uvicorn main:app --reload
```

## License

Proprietary. All rights reserved.
