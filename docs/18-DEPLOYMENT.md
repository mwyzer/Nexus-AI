# 18 — Deployment Specification

## Infrastructure Overview

```
┌────────────────────────────────────────────────────────┐
│                    Docker Compose                       │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │ Next.js  │  │  NestJS  │  │  FastAPI + Celery    │ │
│  │ :3000    │  │  :3001   │  │  :8000 / worker      │ │
│  └──────────┘  └──────────┘  └──────────────────────┘ │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │PostgreSQL│  │  Redis   │  │  Ollama (optional)   │ │
│  │ :5432    │  │  :6379   │  │  :11434              │ │
│  └──────────┘  └──────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

## Docker Compose (Development)

```yaml
# infrastructure/docker-compose.yml

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: nexusai
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: nexusai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nexusai"]
      interval: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 5

  gateway:
    build:
      context: ../gateway
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://nexusai:${DB_PASSWORD}@postgres:5432/nexusai
      - REDIS_URL=redis://redis:6379/0
      - JWT_ACCESS_SECRET=${JWT_ACCESS_SECRET}
      - JWT_REFRESH_SECRET=${JWT_REFRESH_SECRET}
      - AI_BACKEND_URL=http://ai-backend:8000
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../gateway/src:/app/src
    command: npm run start:dev

  ai-backend:
    build:
      context: ../ai-backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://nexusai:${DB_PASSWORD}@postgres:5432/nexusai
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_PUBLIC_KEY=${JWT_PUBLIC_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../ai-backend/app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery-worker:
    build:
      context: ../ai-backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://nexusai:${DB_PASSWORD}@postgres:5432/nexusai
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../ai-backend/app:/app/app
    command: celery -A app.worker.celery_app worker --loglevel=info --concurrency=4

  celery-beat:
    build:
      context: ../ai-backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://nexusai:${DB_PASSWORD}@postgres:5432/nexusai
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - postgres
    command: celery -A app.worker.celery_app beat --loglevel=info

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:3001/api/v1
      - NEXT_PUBLIC_WS_URL=ws://localhost:3001/ws
    depends_on:
      - gateway
    volumes:
      - ../frontend/src:/app/src
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
```

## Dockerfiles

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base
WORKDIR /app

FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

FROM base AS dev
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

### Gateway Dockerfile

```dockerfile
# gateway/Dockerfile
FROM node:20-alpine AS base
WORKDIR /app

FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json .
EXPOSE 3001
CMD ["node", "dist/main"]
```

### AI Backend Dockerfile

```dockerfile
# ai-backend/Dockerfile
FROM python:3.11-slim AS base
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

FROM base AS deps
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-dev

FROM base AS dev
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## Environment Variables

```bash
# .env.example

# Database
DB_PASSWORD=change-me-in-production
DATABASE_URL=postgresql://nexusai:${DB_PASSWORD}@localhost:5432/nexusai

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT (generate with: openssl rand -base64 64)
JWT_ACCESS_SECRET=generate-a-secure-random-secret
JWT_REFRESH_SECRET=generate-another-secure-random-secret
JWT_PUBLIC_KEY=your-rsa-public-key

# AI
OPENAI_API_KEY=sk-...
AI_BACKEND_URL=http://localhost:8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:3001/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:3001/ws

# Optional: Local LLM
OLLAMA_URL=http://localhost:11434
```

## Production Considerations

### Scaling

| Service        | Strategy                          |
|----------------|-----------------------------------|
| Frontend       | CDN + multiple instances          |
| Gateway        | Horizontal with Redis adapter     |
| AI Backend     | Horizontal, stateless             |
| Celery Worker  | Multiple workers, task routing    |
| PostgreSQL     | Read replicas, connection pooling |
| Redis          | Sentinel / Cluster                |

### Monitoring

- **Metrics**: Prometheus + Grafana
- **Logging**: Structured JSON → ELK / Loki
- **Tracing**: OpenTelemetry → Jaeger
- **Alerts**: AlertManager → Slack/PagerDuty

### Health Checks

```
GET /api/v1/admin/health
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ai_backend": "healthy",
    "celery": "4 workers"
  },
  "uptime": "5d 12h 30m"
}
```

### Backup Strategy

| Data            | Frequency | Retention |
|-----------------|-----------|-----------|
| PostgreSQL      | Daily     | 30 days   |
| Redis           | Not needed| N/A       |
| File Storage    | Daily     | 30 days   |
| Config          | On change | Infinite  |
