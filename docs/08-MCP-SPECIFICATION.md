# 08 — MCP (Model Context Protocol) Specification

## Overview

Nexus AI implements both MCP Client and MCP Server roles:

- **MCP Client** — discovers and calls tools from external MCP servers
- **MCP Server** — exposes Nexus AI capabilities as MCP tools

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 Nexus AI Platform                │
│                                                  │
│  ┌──────────────┐          ┌──────────────────┐ │
│  │ MCP Client   │────────→ │ External MCP     │ │
│  │ (Tool User)  │←──────── │ Servers          │ │
│  └──────────────┘          └──────────────────┘ │
│                                                  │
│  ┌──────────────┐          ┌──────────────────┐ │
│  │ MCP Server   │←──────── │ External MCP     │ │
│  │ (Tool Provider)│────────→│ Clients          │ │
│  └──────────────┘          └──────────────────┘ │
└─────────────────────────────────────────────────┘
```

## MCP Client

### Server Connection

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def connect_to_server(server_config: MCPServerConfig) -> ClientSession:
    params = StdioServerParameters(
        command=server_config.command,
        args=server_config.args,
        env=server_config.env,
    )
    
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return session
```

### Tool Discovery

```python
async def discover_tools(session: ClientSession) -> list[Tool]:
    result = await session.list_tools()
    return result.tools
```

### Tool Execution

```python
async def execute_tool(
    session: ClientSession,
    tool_name: str,
    arguments: dict[str, Any],
) -> CallToolResult:
    result = await session.call_tool(tool_name, arguments)
    return result
```

## MCP Server

### Server Definition

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("nexus-ai")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_knowledge_base",
            description="Search Nexus AI knowledge bases",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "kb_id": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["query", "kb_id"],
            },
        ),
        Tool(
            name="run_agent",
            description="Run a Nexus AI agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "task": {"type": "string"},
                },
                "required": ["agent_id", "task"],
            },
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_knowledge_base":
        result = await nexus_search(arguments["query"], arguments["kb_id"])
        return [TextContent(type="text", text=json.dumps(result))]
    # ...
```

## Transport Protocols

| Transport | Description              | Use Case                     |
|-----------|--------------------------|------------------------------|
| stdio     | Standard I/O             | Local CLI tools, subprocess  |
| SSE       | Server-Sent Events       | Remote HTTP servers          |
| WebSocket | Bidirectional streaming  | Real-time, persistent        |

## Tool Registry

```python
class MCPToolRegistry:
    def __init__(self):
        self._servers: dict[str, MCPServerConnection] = {}
        self._tools: dict[str, MCPToolInfo] = {}
    
    async def add_server(self, config: MCPServerConfig) -> None:
        """Connect to an MCP server and register its tools."""
        pass
    
    async def remove_server(self, server_id: str) -> None:
        """Disconnect from server and remove its tools."""
        pass
    
    async def refresh_tools(self) -> None:
        """Re-discover tools from all connected servers."""
        pass
    
    async def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        pass
    
    def list_all_tools(self) -> list[ToolDefinition]:
        """List all available tools from all servers."""
        pass
```

## Security

- All MCP connections use JWT authentication
- Tool access controlled by RBAC
- Input validation on all tool calls
- Rate limiting per tool
- Audit logging for all executions

## Error Handling

```python
class MCPError(Exception): ...
class MCPConnectionError(MCPError): ...
class MCPToolError(MCPError): ...
class MCPTimeoutError(MCPError): ...
class MCPAuthError(MCPError): ...

# Graceful degradation: if a tool fails, agent continues with fallback
```
