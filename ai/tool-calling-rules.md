# Tool Calling Rules

## Tool Definition Standards

### Schema Requirements

Every tool MUST have:
1. **Name** — unique, snake_case identifier
2. **Description** — clear purpose and usage guidance
3. **Input Schema** — JSON Schema with types, descriptions, and required fields
4. **Output Format** — documented return type

### Tool Naming Convention

```
{namespace}_{action}_{target}

Examples:
- kb_search         (knowledge base search)
- file_read          (read file)
- api_call_get       (API GET call)
- db_query_select    (database select query)
- code_execute       (execute code)
```

## Tool Implementation Rules

### 1. Input Validation

```python
@tool
def search_knowledge_base(query: str, kb_id: str, top_k: int = 5) -> str:
    """Search a knowledge base for relevant information.
    
    Args:
        query: The search query string (1-1000 chars)
        kb_id: UUID of the knowledge base to search
        top_k: Number of results to return (1-50, default 5)
    """
    # Validate inputs
    if not query or len(query) > 1000:
        raise ValueError("Query must be 1-1000 characters")
    if top_k < 1 or top_k > 50:
        raise ValueError("top_k must be between 1 and 50")
    
    # Execute
    results = vector_store.search(query, kb_id, top_k)
    return json.dumps([r.model_dump() for r in results])
```

### 2. Error Handling

- Catch and wrap exceptions with descriptive messages
- Never expose internal implementation details in errors
- Return structured error objects
- Log errors for debugging

### 3. Timeouts

- Set reasonable timeouts for all external calls (default: 30s)
- Return partial results on timeout when possible
- Indicate timeout in response

### 4. Rate Limiting

- Respect external API rate limits
- Queue requests when approaching limits
- Report rate limit status to the agent

### 5. Idempotency

- Read operations: always idempotent
- Write operations: prefer idempotent designs
- Use idempotency keys for non-idempotent operations

## Tool Categories

### Knowledge Tools
- `kb_search` — semantic/hybrid search
- `kb_list_documents` — list documents in KB
- `kb_get_document` — read document content

### Data Tools
- `db_query` — execute read-only SQL
- `api_call` — make HTTP API calls
- `file_read` — read file content

### Code Tools
- `code_execute` — execute code in sandbox
- `code_review` — analyze code for issues
- `code_format` — format code

### Utility Tools
- `web_search` — search the web
- `calculator` — perform calculations
- `datetime` — get current date/time
- `text_transform` — transform text (summarize, translate, etc.)

## MCP Tool Integration

MCP tools follow the same rules plus:
- Discover tools on server connection
- Validate against server-provided schema
- Handle server disconnection gracefully
- Cache tool definitions with TTL
