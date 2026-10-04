# 16 — Security Specification

## Security Principles

1. **Defense in Depth** — multiple layers of security controls
2. **Least Privilege** — minimal permissions by default
3. **Secure by Default** — safe defaults, opt-in for less secure
4. **Zero Trust** — verify every request, internal or external
5. **Fail Secure** — errors default to denying access

## Authentication Security

### Password Policy

- Minimum 8 characters (enforced by gateway DTOs and frontend validation)
- *Planned hardening:* minimum 12 characters, uppercase/lowercase/number/special, account lockout after 5 failed attempts (15 min), password history (no reuse of last 5)
- Bcrypt hashing with cost factor 12

### JWT Security

```
Access Token:
- RS256 algorithm (asymmetric)
- 15-minute expiry
- Short-lived, not stored

Refresh Token:
- 256-bit random string
- Hashed with SHA-256 before storage
- 7-day expiry, rotated on use
- Stored in Redis for revocation
- Tied to device fingerprint
```

### Session Management

```typescript
interface SessionConfig {
  maxConcurrentSessions: 5;
  idleTimeout: 30 * 60 * 1000;  // 30 minutes
  absoluteTimeout: 8 * 3600 * 1000;  // 8 hours
  extendOnActivity: true;
}
```

## API Security

### Rate Limiting

```
/api/v1/auth/login     →  5 req/min per IP
/api/v1/auth/register  →  3 req/min per IP
/api/v1/*              →  100 req/min per user
/api/v1/agent/run      →  10 req/min per user
```

### Input Validation

- All inputs validated with Zod (NestJS) or Pydantic (FastAPI)
- SQL injection prevention via parameterized queries
- XSS prevention via output encoding
- File upload: type validation, size limits, virus scanning

### CORS Configuration

```typescript
const corsOptions = {
  origin: process.env.ALLOWED_ORIGINS?.split(','),
  methods: ['GET', 'POST', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400,
};
```

## Data Security

### Encryption at Rest

| Data              | Encryption             |
|-------------------|------------------------|
| Passwords         | bcrypt (one-way hash)  |
| API Keys          | AES-256-GCM            |
| Refresh Tokens    | SHA-256 (hash)         |
| PII               | AES-256-GCM            |
| File Storage      | AES-256 (if local)     |

### Encryption in Transit

- TLS 1.3 minimum for all communications
- HSTS with max-age=31536000, includeSubDomains
- Internal service communication over TLS (mTLS in production)

### Data Retention

| Data Type         | Retention      |
|-------------------|----------------|
| Audit Logs        | Configurable   |
| Messages          | 90 days        |
| Deleted Resources | 30 days (soft) |
| Sessions          | Until expiry   |

## Dependency Security

- Dependabot / Renovate for automated updates
- `npm audit` / `pip-audit` in CI pipeline
- Snyk or Trivy for container scanning
- Lock files committed (`package-lock.json`, `poetry.lock`)

## Container Security

```dockerfile
# Best practices
FROM node:20-alpine  # Minimal base image
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs  # Non-root user
COPY --chown=nodejs:nodejs . .
```

## Secret Management

```
# NEVER in code or config files
# Development: .env (in .gitignore)
# Production: Docker secrets / HashiCorp Vault / AWS Secrets Manager

.env.example (committed):
JWT_ACCESS_SECRET=generate-a-random-secret
DATABASE_URL=postgresql://user:password@localhost:5432/nexusai
REDIS_URL=redis://localhost:6379/0
```

## Security Headers (Helmet)

```typescript
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
}));
```

## Incident Response

1. **Detect** — monitoring, alerts, user reports
2. **Contain** — revoke tokens, isolate affected systems
3. **Investigate** — audit logs, forensic analysis
4. **Remediate** — patch, restore, harden
5. **Report** — notify affected users within 72 hours
6. **Review** — post-mortem, process improvement
