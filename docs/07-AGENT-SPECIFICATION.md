# 07 — Agent Specification

## Agent Architecture (LangGraph)

```
┌────────────────────────────────────────────────┐
│                   Agent Runtime                 │
│                                                 │
│  ┌──────────┐   ┌──────────┐   ┌────────────┐ │
│  │  Planner  │ → │ Executor  │ → │  Evaluator  │ │
│  └──────────┘   └──────────┘   └────────────┘ │
│       ↑               │               │         │
│       └───────────────┴───────────────┘         │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │              Tool Registry                 │  │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────────┐  │  │
│  │  │Search│ │Code│ │API │ │DB  │ │Custom  │  │  │
│  │  └────┘ └────┘ └────┘ └────┘ └────────┘  │  │
│  └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

## Agent Graph (LangGraph)

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

class AgentState(TypedDict):
    messages: list[BaseMessage]
    task: str
    plan: list[PlanStep] | None
    current_step: int
    tool_results: dict[str, Any]
    final_output: str | None
    is_complete: bool

def create_agent_graph(tools: list[BaseTool], llm: BaseChatModel) -> StateGraph:
    workflow = StateGraph(AgentState)
    
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("tools", ToolExecutor(tools))
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("synthesize", synthesize_node)
    
    workflow.set_entry_point("plan")
    workflow.add_conditional_edges("plan", should_continue, {
        "execute": "execute",
        "synthesize": "synthesize",
    })
    workflow.add_edge("execute", "tools")
    workflow.add_edge("tools", "evaluate")
    workflow.add_conditional_edges("evaluate", should_continue, {
        "execute": "execute",
        "synthesize": "synthesize",
    })
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()
```

## Tool Calling

### Tool Definition

```python
from langchain.tools import tool

@tool
def search_knowledge_base(query: str, kb_id: str) -> str:
    """Search the knowledge base for relevant information.
    
    Args:
        query: The search query string
        kb_id: The knowledge base ID to search in
    """
    # Implementation
    pass

@tool
def execute_code(code: str, language: str = "python") -> str:
    """Execute code in a sandboxed environment.
    
    Args:
        code: The code to execute
        language: Programming language (python, javascript)
    """
    # Implementation
    pass
```

### Tool Registry

```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._mcp_tools: dict[str, MCPTool] = {}
    
    def register(self, tool: BaseTool) -> None: ...
    def register_mcp(self, tool: MCPTool) -> None: ...
    def get(self, name: str) -> BaseTool: ...
    def list_tools(self) -> list[ToolDefinition]: ...
    def execute(self, name: str, **kwargs) -> Any: ...
```

## Agent Types

### 1. RAG Agent
- Answers questions from knowledge bases
- Cites sources
- Follows up for clarification

### 2. Tool-Using Agent
- Plans and executes multi-step tasks
- Uses tools to gather information
- Iterates until task completion

### 3. Chat Agent
- Conversational with memory
- Context-aware responses
- No tool access (by default)

### 4. Custom Agent
- User-defined system prompt
- Configurable tool set
- Custom graph definition

## Conversation Memory

```python
class ConversationMemory:
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
    
    def add_message(self, message: BaseMessage) -> None:
        # Add message, trim if exceeding max_tokens
        pass
    
    def get_context(self) -> list[BaseMessage]:
        # Return recent messages within token limit
        pass
    
    def summarize(self) -> str:
        # Generate conversation summary
        pass
```

### Memory Types

| Type               | Description                        |
|--------------------|------------------------------------|
| Buffer             | Fixed-size sliding window          |
| Summary            | Summarize older messages           |
| Buffer + Summary   | Recent + summary of older          |
| Vector-Backed      | Semantic retrieval from history    |

## Agent Templates

Pre-built agent configurations:

```json
{
  "name": "Code Assistant",
  "description": "Helps write, review, and debug code",
  "system_prompt": "You are an expert software engineer...",
  "model": "gpt-4o",
  "tools": ["search_kb", "execute_code", "read_file"],
  "memory_type": "buffer_summary",
  "max_iterations": 10
}
```

## Evaluation

| Metric              | Description                              |
|---------------------|------------------------------------------|
| Task Completion     | Did agent complete the task?             |
| Tool Accuracy       | Were tools called with correct params?   |
| Efficiency          | Steps used vs minimum steps needed       |
| Output Quality      | Human eval of final output               |
| Failure Recovery    | Did agent recover from tool errors?      |
