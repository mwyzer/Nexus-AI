# 09 — Authentication & RBAC Specification

## Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │     │ Gateway  │     │   DB     │     │  Redis   │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ POST /login    │                │                │
     │───────────────→│                │                │
     │                │ SELECT user    │                │
     │                │───────────────→│                │
     │                │←───────────────│                │
     │                │ Verify hash    │                │
     │                │ Generate JWT   │                │
     │                │ Store refresh  │                │
     │                │───────────────────────────────→│
     │ {access,       │                │                │
     │  refresh}      │                │                │
     │←───────────────│                │                │
```

## JWT Configuration

```typescript
// gateway/src/auth/jwt.config.ts
export const jwtConfig = {
  access: {
    secret: process.env.JWT_ACCESS_SECRET!,
    expiresIn: '15m',
  },
  refresh: {
    secret: process.env.JWT_REFRESH_SECRET!,
    expiresIn: '7d',
    rotateEvery: '1d',
  },
};

// JWT Payload
interface JwtPayload {
  sub: string;        // user UUID
  email: string;
  roles: string[];
  iat: number;
  exp: number;
}
```

## NestJS Auth Guards

```typescript
// JWT Guard
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}

// Role Guard
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}
  
  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.get<string[]>('roles', context.getHandler());
    if (!requiredRoles) return true;
    
    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.some(role => user.roles?.includes(role));
  }
}

// ACL Guard
@Injectable()
export class AclGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const requiredPermission = this.reflector.get<Permission>('permission', context.getHandler());
    if (!requiredPermission) return true;
    
    const { user, params } = context.switchToHttp().getRequest();
    return this.aclService.check(user.id, requiredPermission, params.id);
  }
}

// Usage
@Controller('knowledge-bases')
@UseGuards(JwtAuthGuard, RolesGuard)
export class KnowledgeBaseController {
  
  @Get()
  @Roles('admin', 'editor', 'viewer')
  findAll() {}
  
  @Delete(':id')
  @Roles('admin')
  @Acl({ resource: 'knowledge_base', action: 'delete' })
  remove(@Param('id') id: string) {}
}
```

## RBAC Roles

| Role      | Permissions                                    |
|-----------|------------------------------------------------|
| `admin`   | Full system access, user management            |
| `editor`  | Create/edit knowledge bases, agents, tools     |
| `viewer`  | Read-only access to assigned resources         |
| `api`     | Programmatic access with API keys              |

## Default Permissions

```typescript
enum Permission {
  // Knowledge Bases
  KB_CREATE = 'kb:create',
  KB_READ = 'kb:read',
  KB_UPDATE = 'kb:update',
  KB_DELETE = 'kb:delete',
  
  // Documents
  DOC_UPLOAD = 'doc:upload',
  DOC_DELETE = 'doc:delete',
  
  // Agents
  AGENT_CREATE = 'agent:create',
  AGENT_READ = 'agent:read',
  AGENT_UPDATE = 'agent:update',
  AGENT_DELETE = 'agent:delete',
  AGENT_RUN = 'agent:run',
  
  // MCP
  MCP_SERVER_MANAGE = 'mcp:manage',
  MCP_TOOL_EXECUTE = 'mcp:execute',
  
  // Admin
  USER_MANAGE = 'user:manage',
  AUDIT_READ = 'audit:read',
  SYSTEM_CONFIG = 'system:config',
}
```

## ACL Model

```typescript
interface AclEntry {
  userId: string;
  resourceType: string;
  resourceId: string;
  permissions: string[];  // ['read', 'write', 'delete']
}
```

## Security Best Practices

1. **Password hashing** — bcrypt with cost factor 12
2. **Token rotation** — refresh tokens rotate on use
3. **Token revocation** — stored in Redis blacklist
4. **Rate limiting** — login: 5 attempts/minute per IP
5. **CSRF protection** — SameSite cookies, CSRF tokens
6. **CORS** — strict origin whitelist
7. **Headers** — Helmet.js for security headers
8. **Input validation** — Zod/Pydantic on all inputs
9. **SQL injection** — parameterized queries only
10. **HTTPS only** — HSTS enforced in production
