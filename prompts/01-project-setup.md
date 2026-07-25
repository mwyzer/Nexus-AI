# Prompt: Project Setup

Use this prompt when initializing the project structure or setting up new services.

---

## Instructions

Set up the Nexus AI monorepo with the following structure. Follow the tech stack and principles defined in README.md and docs/02-TECHNICAL-SPECIFICATION.md.

### Monorepo Root
```
nexus-ai/
├── frontend/          # Next.js 14 + TypeScript + Tailwind + shadcn/ui
├── gateway/           # NestJS + TypeScript + Socket.IO
├── ai-backend/        # Python + FastAPI + Pydantic
├── infrastructure/    # Docker Compose files
├── scripts/           # Setup and utility scripts
├── docs/              # Documentation
├── .github/           # CI/CD workflows
├── .env.example       # Environment variable template
├── .gitignore
└── README.md
```

### Requirements

1. **Frontend**:
   - Use `create-next-app` with TypeScript, Tailwind, App Router
   - Install shadcn/ui with `npx shadcn-ui@latest init`
   - Configure path alias `@/` → `src/`
   - Set up Zustand for state, React Query for server state
   - Create base layout with dark mode

2. **Gateway**:
   - Use `@nestjs/cli` to scaffold
   - Configure TypeORM or Prisma with PostgreSQL
   - Set up modules: auth, users, common (guards, decorators, filters)
   - Configure validation pipe, CORS, Helmet

3. **AI Backend**:
   - Use Poetry for dependency management
   - Set up FastAPI with async SQLAlchemy + pgvector
   - Configure Alembic for migrations
   - Set up Celery with Redis broker

4. **Infrastructure**:
   - Docker Compose with all services
   - Health checks on all services
   - Hot reload volumes for development

5. **CI/CD**:
   - GitHub Actions workflow for lint, type-check, tests

### Key Rules
- Never commit `.env` files
- Use `.env.example` with placeholder values
- All services must have health check endpoints
- Use strict TypeScript and Python type hints
- Follow the module structure defined in the docs
