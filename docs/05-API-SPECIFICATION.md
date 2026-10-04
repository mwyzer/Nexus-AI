# 05 — API Specification

## Base URLs

| Service    | Base URL                    |
|------------|-----------------------------|
| Gateway    | `http://localhost:3001/api/v1` |
| AI Backend | `http://localhost:8000/api/v1` |
| WebSocket  | `ws://localhost:3001/ws`       |

## API Gateway Endpoints

### Authentication

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
```

### Users (Admin) — *planned (Phase 05)*

```
GET    /api/v1/users
GET    /api/v1/users/:id
PATCH  /api/v1/users/:id
DELETE /api/v1/users/:id
POST   /api/v1/users/:id/roles
```

### Knowledge Bases

```
GET    /api/v1/knowledge-bases
POST   /api/v1/knowledge-bases
GET    /api/v1/knowledge-bases/:id
PATCH  /api/v1/knowledge-bases/:id
DELETE /api/v1/knowledge-bases/:id
```

### Documents

```
POST   /api/v1/documents        multipart form: knowledge_base_id + file
GET    /api/v1/documents?knowledgeBaseId=:kbId
GET    /api/v1/documents/:id
DELETE /api/v1/documents/:id
```

### Search

```
POST   /api/v1/search           JSON body: query, knowledge_base_id, search_type, top_k
```

### Health

```
GET    /api/v1/health
```

### Agents — *planned (Phase 03)*

```
GET    /api/v1/agents
POST   /api/v1/agents
GET    /api/v1/agents/:id
PATCH  /api/v1/agents/:id
DELETE /api/v1/agents/:id
POST   /api/v1/agents/:id/run
```

### Conversations — *planned (Phase 03)*

```
GET    /api/v1/conversations
POST   /api/v1/conversations
GET    /api/v1/conversations/:id
POST   /api/v1/conversations/:id/messages
DELETE /api/v1/conversations/:id
```

### MCP — *planned (Phase 04)*

```
GET    /api/v1/mcp/servers
POST   /api/v1/mcp/servers
GET    /api/v1/mcp/servers/:id/tools
POST   /api/v1/mcp/tools/:id/execute
```

### Audit & Admin — *planned (Phase 05)*

```
GET    /api/v1/audit-logs
GET    /api/v1/admin/metrics
GET    /api/v1/admin/health
```

## AI Backend Endpoints (Internal)

### RAG

```
POST   /api/v1/documents        document upload (multipart) → triggers async ingestion
DELETE /api/v1/documents/:id
POST   /api/v1/search
POST   /api/v1/rag/generate
```

### Agent — *planned (Phase 03)*

```
POST   /api/v1/agent/run
POST   /api/v1/agent/stream
GET    /api/v1/agent/:id/status
POST   /api/v1/agent/:id/cancel
```

### Embeddings — *planned (Phase 02/06)*

```
POST   /api/v1/embeddings/generate
POST   /api/v1/embeddings/batch
```

### Evaluation — *planned (Phase 06)*

```
POST   /api/v1/eval/rag
POST   /api/v1/eval/agent
GET    /api/v1/eval/runs
GET    /api/v1/eval/runs/:id
```

## Standard Response Format

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

## Error Response Format

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

## HTTP Status Codes

| Code | Usage                                    |
|------|------------------------------------------|
| 200  | Success                                   |
| 201  | Created                                   |
| 204  | No Content (successful delete)           |
| 400  | Bad Request / Validation Error           |
| 401  | Unauthorized (missing/invalid token)      |
| 403  | Forbidden (insufficient permissions)      |
| 404  | Not Found                                 |
| 409  | Conflict (duplicate resource)            |
| 429  | Rate Limited                              |
| 500  | Internal Server Error                     |

## WebSocket Events

### Client → Server

```
conversation:join     { conversationId }
conversation:message  { content, attachments }
agent:run             { agentId, input }
agent:cancel          { runId }
```

### Server → Client

```
conversation:message  { id, role, content, metadata }
conversation:token    { content, done }
agent:step            { step, thought, action, observation }
agent:complete        { runId, output }
agent:error           { runId, error }
notification:info     { title, message }
```

## Pagination

Query parameters: `?page=1&per_page=20&sort=created_at&order=desc`

Response includes `meta` object with `page`, `per_page`, `total`, `total_pages`.
