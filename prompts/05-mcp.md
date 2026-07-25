# Prompt: MCP Implementation

Use this prompt when implementing MCP Client and Server features.

---

## Instructions

### MCP Client Setup
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClientManager:
    def __init__(self):
        self._connections: dict[str, ClientSession] = {}
        self._tools: dict[str, MCPTool] = {}
    
    async def connect(self, config: MCPServerConfig) -> None:
        """Connect to an MCP server and discover its tools."""
        params = StdioServerParameters(
            command=config.command,
            args=config.args,
            env=config.env,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                for tool in tools.tools:
                    self._tools[f"{config.name}:{tool.name}"] = MCPTool(
                        session=session,
                        definition=tool,
                    )
                self._connections[config.name] = session
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute an MCP tool."""
        tool = self._tools[tool_name]
        result = await tool.session.call_tool(tool.definition.name, kwargs)
        return result
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
            name="nexus_search",
            description="Search Nexus AI knowledge bases",
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
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handlers = {
        "nexus_search": handle_search,
        "nexus_run_agent": handle_run_agent,
    }
    result = await handlers[name](arguments)
    return [TextContent(type="text", text=json.dumps(result))]
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
