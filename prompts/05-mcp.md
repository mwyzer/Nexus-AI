# Prompt: MCP Implementation

Use this prompt when implementing MCP Client and Server features.

---

## Instructions

### Shared Primitives

```python
import time
from dataclasses import dataclass, field
from typing import Any
from mcp import ClientSession
from mcp.types import Tool

@dataclass
class MCPTool:
    session: ClientSession
    definition: Tool
    cached_at: float = field(default_factory=time.monotonic)

class TokenBucket:
    """Simple token bucket used for client- and server-side rate limiting."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens refilled per second
        self.capacity = capacity
        self.tokens = float(capacity)
        self.updated_at = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.updated_at) * self.rate)
        self.updated_at = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

class RateLimitExceeded(Exception):
    pass
```

### MCP Client Setup

```python
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

audit_log = logging.getLogger("mcp.audit")

class MCPClientManager:
    TOOL_CACHE_TTL_SECONDS = 300  # 5 min, per Key Rules

    def __init__(self):
        self._connections: dict[str, ClientSession] = {}
        self._stacks: dict[str, AsyncExitStack] = {}
        self._tools: dict[str, MCPTool] = {}
        self._limiters: dict[str, TokenBucket] = {}

    async def connect(self, config: MCPServerConfig) -> None:
        """Connect to an MCP server over stdio and discover its tools.

        Uses an AsyncExitStack per server so the stdio transport and
        session stay open after this method returns, instead of being
        torn down by exiting `async with` blocks here.
        """
        stack = AsyncExitStack()
        try:
            params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env,
            )
            read, write = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            await self._register_tools(config.name, session)
            self._connections[config.name] = session
            self._stacks[config.name] = stack
        except Exception:
            await stack.aclose()
            raise

    async def disconnect(self, server_name: str) -> None:
        """Close the transport and session for a server, and drop its cached state."""
        stack = self._stacks.pop(server_name, None)
        self._connections.pop(server_name, None)
        self._limiters.pop(server_name, None)
        self._tools = {k: v for k, v in self._tools.items() if not k.startswith(f"{server_name}:")}
        if stack is not None:
            await stack.aclose()

    async def _register_tools(self, server_name: str, session: ClientSession) -> None:
        """Replace the cached tool set for a server (drops tools the server no longer exposes)."""
        tools = await session.list_tools()
        now = time.monotonic()
        self._tools = {k: v for k, v in self._tools.items() if not k.startswith(f"{server_name}:")}
        for tool in tools.tools:
            self._tools[f"{server_name}:{tool.name}"] = MCPTool(
                session=session, definition=tool, cached_at=now,
            )

    async def get_tools(self, server_name: str) -> list[MCPTool]:
        """Return cached tool definitions for a server, refreshing if stale."""
        server_tools = [t for k, t in self._tools.items() if k.startswith(f"{server_name}:")]
        now = time.monotonic()
        is_stale = not server_tools or any(
            now - t.cached_at > self.TOOL_CACHE_TTL_SECONDS for t in server_tools
        )
        if is_stale:
            await self._register_tools(server_name, self._connections[server_name])
            server_tools = [t for k, t in self._tools.items() if k.startswith(f"{server_name}:")]
        return server_tools

    async def execute_tool(self, tool_name: str, timeout: float = 30.0, **kwargs) -> Any:
        """Execute an MCP tool with a timeout (default: 30s), rate limiting, and audit logging."""
        server_name = tool_name.split(":", 1)[0]
        limiter = self._limiters.setdefault(server_name, TokenBucket(rate=5, capacity=10))
        if not limiter.allow():
            raise RateLimitExceeded(server_name)

        tool = self._tools[tool_name]
        started = time.monotonic()
        try:
            result = await asyncio.wait_for(
                tool.session.call_tool(tool.definition.name, kwargs),
                timeout=timeout,
            )
            audit_log.info(
                "mcp_tool_call", server=server_name, tool=tool_name,
                duration_ms=(time.monotonic() - started) * 1000, status="ok",
            )
            return result
        except Exception as exc:
            audit_log.error(
                "mcp_tool_call", server=server_name, tool=tool_name,
                duration_ms=(time.monotonic() - started) * 1000,
                status="error", error=str(exc),
            )
            raise
```

### SSE Transport (Client)

```python
from mcp.client.sse import sse_client

class MCPClientManager:
    async def connect_sse(self, config: MCPServerConfig) -> None:
        """Connect to an MCP server over SSE, authenticating with a JWT.

        The JWT is sent once as a header on the SSE handshake — the server
        verifies it when the connection is established, not on every tool call.
        """
        stack = AsyncExitStack()
        try:
            headers = {"Authorization": f"Bearer {config.jwt_token}"}
            read, write = await stack.enter_async_context(
                sse_client(config.url, headers=headers)
            )
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            await self._register_tools(config.name, session)
            self._connections[config.name] = session
            self._stacks[config.name] = stack
        except Exception:
            await stack.aclose()
            raise
```

### Server Configuration (mcp.json)

The set of external MCP servers to connect to is declared in `ai-backend/mcp.json`
(mounted into the container at `/app/mcp.json`, path given by `MCP_SERVERS_CONFIG`),
using the same `mcpServers` shape as Claude Desktop/Cursor/VS Code configs:

```json
{
  "mcpServers": {
    "some-server": {
      "transport": "stdio",
      "command": "docker",
      "args": ["run", "--rm", "-i", "<image>"],
      "env": {},
      "enabled": true
    }
  }
}
```

```python
import json
from pydantic import BaseModel

class MCPServerConfig(BaseModel):
    name: str
    transport: Literal["stdio", "sse"]
    command: str | None = None
    args: list[str] = []
    env: dict[str, str] = {}
    url: str | None = None
    jwt_token: str | None = None
    enabled: bool = True

def load_server_configs(path: str) -> list[MCPServerConfig]:
    raw = json.loads(Path(path).read_text())
    return [
        MCPServerConfig(name=name, **cfg)
        for name, cfg in raw.get("mcpServers", {}).items()
        if cfg.get("enabled", True) and not name.startswith("_")
    ]

async def connect_all(manager: MCPClientManager) -> None:
    """Called on app startup to connect every configured, enabled server."""
    for config in load_server_configs(settings.mcp_servers_config_path):
        if config.transport == "stdio":
            await manager.connect(config)
        else:
            await manager.connect_sse(config)
```

### MCP Server Setup

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("nexus-ai")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_knowledge_base",
            description="Search a Nexus AI knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "kb_id": {"type": "string", "description": "Knowledge base ID"},
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["query", "kb_id"],
            },
        ),
        Tool(
            name="list_knowledge_bases",
            description="List knowledge bases available to the caller",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="run_agent",
            description="Run a Nexus AI agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent ID"},
                    "input": {"type": "string", "description": "Input message for the agent"},
                },
                "required": ["agent_id", "input"],
            },
        ),
        Tool(
            name="list_agents",
            description="List agents available to the caller",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # No auth_token parameter here: the SDK invokes this with just
    # (name, arguments). JWT verification already happened once at the
    # SSE handshake (see below) — stdio connections are a trusted local
    # subprocess and skip JWT entirely.
    handlers = {
        "search_knowledge_base": handle_search_knowledge_base,
        "list_knowledge_bases": handle_list_knowledge_bases,
        "run_agent": handle_run_agent,
        "list_agents": handle_list_agents,
    }
    validate_tool_input(name, arguments)
    enforce_rate_limit(name)

    started = time.monotonic()
    try:
        result = await asyncio.wait_for(handlers[name](arguments), timeout=30.0)
        audit_log.info(
            "mcp_tool_served", tool=name,
            duration_ms=(time.monotonic() - started) * 1000, status="ok",
        )
        return [TextContent(type="text", text=json.dumps(result))]
    except Exception as exc:
        audit_log.error(
            "mcp_tool_served", tool=name,
            duration_ms=(time.monotonic() - started) * 1000,
            status="error", error=str(exc),
        )
        raise
```

### SSE Transport & JWT Auth (Server)

Mounted onto the existing `ai-backend` FastAPI app (`app/main.py`) — MCP runs
in the same process and port (8000) as the rest of the API, reusing the
platform's own access-token secret rather than a separate MCP credential.

```python
from jose import JWTError, jwt
from jsonschema import validate as validate_schema, ValidationError
from starlette.requests import Request
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
from .config import settings

sse_transport = SseServerTransport("/mcp/messages")

async def handle_sse(request: Request):
    """Verify the platform JWT once, at the SSE handshake -- not per tool call."""
    auth_header = request.headers.get("authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        jwt.decode(token, settings.jwt_access_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return Response(status_code=401)

    async with sse_transport.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await server.run(read, write, server.create_initialization_options())

# in app/main.py: app.add_route("/mcp/sse", handle_sse)

TOOL_SCHEMAS: dict[str, dict] = {}  # populated from each Tool.inputSchema in list_tools()

def validate_tool_input(name: str, arguments: dict) -> None:
    schema = TOOL_SCHEMAS.get(name)
    if schema is None:
        raise ValueError(f"Unknown tool: {name}")
    try:
        validate_schema(instance=arguments, schema=schema)
    except ValidationError as exc:
        raise ValueError(f"Invalid arguments for {name}: {exc.message}") from exc

_tool_limiters: dict[str, TokenBucket] = {}

def enforce_rate_limit(tool_name: str, rate: float = 10, capacity: int = 20) -> None:
    limiter = _tool_limiters.setdefault(tool_name, TokenBucket(rate=rate, capacity=capacity))
    if not limiter.allow():
        raise PermissionError(f"Rate limit exceeded for tool: {tool_name}")
```

### Key Rules
- Support both stdio and SSE transports
- Authenticate MCP connections with JWT
- Validate all tool inputs against schemas
- Set timeouts for tool execution (default: 30s)
- Handle server disconnection gracefully
- Cache tool definitions with TTL (default: 5 min)
- Log all tool executions for audit
- Rate limit tool calls per server
