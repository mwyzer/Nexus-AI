# Phase 01 — Project Foundation

## Goal

Set up the monorepo structure with all three services (Frontend, API Gateway, AI Backend), Docker Compose for local development, database schemas, authentication, and CI pipeline.

## Tasks

### 1.1 — Monorepo Scaffolding
- [x] Initialize root `package.json` with workspaces
- [x] Create `.gitignore` (node_modules, .env, __pycache__, etc.)
- [x] Create `.env.example` with all required variables
- [x] Create `.editorconfig` for consistent formatting
- [x] Set up ESLint + Prettier config at root

### 1.2 — Frontend Setup (Next.js)
- [x] `npx create-next-app@latest frontend --typescript --tailwind --app`
- [x] Install and configure shadcn/ui
- [x] Set up project structure
- [x] Configure path aliases (`@/` → `src/`)
- [x] Set up Zustand store skeleton
- [x] Set up React Query provider
- [x] Create base layout with dark mode support
- [x] Create placeholder pages: `/`, `/login`, `/register`, `/dashboard`
- [x] Set up Vitest + React Testing Library

### 1.3 — API Gateway Setup (NestJS)
- [x] Set up project structure
- [x] Configure TypeORM with PostgreSQL
- [x] Implement JWT authentication module
- [x] Create RBAC guard and decorator
- [x] Set up global exception filter
- [x] Set up validation pipe (class-validator)
- [x] Set up logging interceptor
- [x] Create health check endpoint
- [x] Configure CORS
- [x] Configure Helmet for security headers

### 1.4 — AI Backend Setup (FastAPI)
- [x] Set up Poetry project
- [x] Configure FastAPI with CORS, middleware
- [x] Set up async SQLAlchemy with PostgreSQL + pgvector
- [x] Set up Alembic for migrations
- [x] Create initial database models (User)
- [x] Set up Pydantic Settings for configuration
- [x] Create health check endpoint
- [x] Set up Celery app skeleton
- [x] Set up Pytest with async support

### 1.5 — Docker Compose
- [x] Create `infrastructure/docker-compose.yml`
- [x] Create health checks for all services
- [x] Create volume mounts for hot reload in dev
- [x] Create `scripts/` for setup and seed

### 1.6 — Database Migrations & Seed
- [x] Create seed script for default roles (admin, editor, viewer)
- [x] Create seed script for default permissions

### 1.7 — Authentication (Full Implementation)
- [x] **Gateway**: Register endpoint with password hashing
- [x] **Gateway**: Login endpoint returning JWT pair
- [x] **Gateway**: Refresh token endpoint
- [x] **Gateway**: Logout (token revocation)
- [x] **Gateway**: Get current user (`/auth/me`)
- [x] **Gateway**: JWT guard for protected routes
- [x] **Gateway**: Roles guard for role-based access
- [x] **AI Backend**: JWT validation dependency
- [x] **Frontend**: Login page with form validation
- [x] **Frontend**: Register page
- [x] **Frontend**: Auth store (Zustand) with token management
- [x] **Frontend**: Protected route wrapper
- [x] **Frontend**: Axios interceptor for token refresh

### 1.8 — CI Pipeline
- [x] Create `.github/workflows/ci.yml`
- [x] Lint job (all services)
- [x] Type-check job
- [x] Unit test job (all services)
- [x] Build check

## Acceptance Criteria

- [x] `docker compose up` starts all services (infrastructure ready)
- [x] Frontend loads at http://localhost:3000 (scaffolded)
- [x] Gateway health check returns 200 at http://localhost:3001/api/v1/health (implemented)
- [x] AI Backend health check returns 200 at http://localhost:8000/api/v1/health (implemented)
- [x] User can register, login, and access protected routes (implemented)
- [x] JWT tokens work correctly (access + refresh flow) (implemented)
- [x] All services hot-reload in development (Docker configs ready)
- [x] CI pipeline passes (lint, type-check, tests) (workflow created)

## Dependencies

None — this is the foundation phase.

## Estimated Effort

3-5 days for a single developer.
