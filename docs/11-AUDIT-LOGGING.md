# 11 — Audit Logging Specification

## Overview

Comprehensive audit logging tracks all significant actions across the Nexus AI platform for security, compliance, and debugging.

## Architecture

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Gateway │    │  AI      │    │  Celery  │
│  Actions │    │  Backend │    │  Workers │
└────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │
     └───────────────┼───────────────┘
                     │
              ┌──────▼──────┐
              │ Audit Queue │ (Redis)
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ Audit Worker│ (Celery)
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ PostgreSQL  │
              └─────────────┘
```

## Audit Events

### Authentication Events

| Action              | Description                    | Severity |
|---------------------|--------------------------------|----------|
| `auth.login`        | User login attempt             | INFO     |
| `auth.login_failed` | Failed login                   | WARN     |
| `auth.logout`       | User logout                    | INFO     |
| `auth.token_refresh`| Token refreshed                | DEBUG    |
| `auth.password_changed` | Password change            | INFO     |

### User Management Events

| Action                     | Description              | Severity |
|----------------------------|--------------------------|----------|
| `user.created`             | User account created     | INFO     |
| `user.updated`             | User profile updated     | INFO     |
| `user.deleted`             | User account deleted     | WARN     |
| `user.role_assigned`       | Role assigned to user    | INFO     |
| `user.role_revoked`        | Role revoked from user   | INFO     |

### Knowledge Base Events

| Action                     | Description              | Severity |
|----------------------------|--------------------------|----------|
| `kb.created`               | Knowledge base created   | INFO     |
| `kb.updated`               | Knowledge base updated   | INFO     |
| `kb.deleted`               | Knowledge base deleted   | WARN     |
| `kb.document_uploaded`     | Document uploaded        | INFO     |
| `kb.document_deleted`      | Document deleted         | INFO     |
| `kb.document_processed`    | Document processing done | DEBUG    |

### Agent Events

| Action                     | Description              | Severity |
|----------------------------|--------------------------|----------|
| `agent.created`            | Agent created             | INFO     |
| `agent.updated`            | Agent updated             | INFO     |
| `agent.deleted`            | Agent deleted             | WARN     |
| `agent.run_started`        | Agent execution started   | INFO     |
| `agent.run_completed`      | Agent execution completed | INFO     |
| `agent.run_failed`         | Agent execution failed    | ERROR    |

### MCP Events

| Action                     | Description              | Severity |
|----------------------------|--------------------------|----------|
| `mcp.server_added`         | MCP server connected     | INFO     |
| `mcp.server_removed`       | MCP server disconnected  | INFO     |
| `mcp.tool_executed`        | MCP tool called          | DEBUG    |
| `mcp.tool_failed`          | MCP tool call failed     | ERROR    |

### Security Events

| Action                     | Description              | Severity |
|----------------------------|--------------------------|----------|
| `security.rate_limited`    | Rate limit hit           | WARN     |
| `security.access_denied`   | Unauthorized access      | WARN     |
| `security.suspicious`      | Suspicious activity      | CRITICAL |

## NestJS Audit Interceptor

```typescript
@Injectable()
export class AuditInterceptor implements NestInterceptor {
  constructor(private auditService: AuditService) {}
  
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const { user, method, url, ip, headers } = request;
    
    const startTime = Date.now();
    
    return next.handle().pipe(
      tap({
        next: (data) => {
          this.auditService.log({
            userId: user?.sub,
            action: this.inferAction(method, url),
            resourceType: this.inferResource(url),
            resourceId: data?.id,
            details: { statusCode: 200, duration: Date.now() - startTime },
            ipAddress: ip,
            userAgent: headers['user-agent'],
          });
        },
        error: (error) => {
          this.auditService.log({
            userId: user?.sub,
            action: this.inferAction(method, url),
            resourceType: this.inferResource(url),
            details: { error: error.message, statusCode: error.status },
            ipAddress: ip,
            userAgent: headers['user-agent'],
          });
        },
      }),
    );
  }
}
```

## Python Audit Client

```python
class AuditLogger:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def log(
        self,
        action: str,
        resource_type: str,
        user_id: UUID | None = None,
        resource_id: UUID | None = None,
        details: dict = {},
        severity: str = "INFO",
    ) -> None:
        event = AuditEvent(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            severity=severity,
            timestamp=datetime.utcnow(),
        )
        await self.redis.lpush("audit:queue", event.model_dump_json())
```

## Query Interface

```sql
-- Search audit logs
SELECT * FROM audit_logs
WHERE user_id = $1
  AND action = $2
  AND created_at BETWEEN $3 AND $4
ORDER BY created_at DESC
LIMIT $5 OFFSET $6;
```

## Retention Policy

| Severity | Retention |
|----------|-----------|
| DEBUG    | 30 days   |
| INFO     | 90 days   |
| WARN     | 1 year    |
| ERROR    | 2 years   |
| CRITICAL | 7 years   |
