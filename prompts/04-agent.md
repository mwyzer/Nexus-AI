# Prompt: Agent Implementation

Use this prompt when implementing agent features with LangGraph.

---

## Instructions

### Agent Graph Structure

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# State
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    task: str
    plan: list[PlanStep] | None
    current_step: int
    iteration_count: int
    tool_results: dict
    final_output: str | None
    error: str | None

# Nodes
def plan_node(state: AgentState) -> AgentState: ...
def execute_node(state: AgentState) -> AgentState: ...
def evaluate_node(state: AgentState) -> AgentState: ...
def synthesize_node(state: AgentState) -> AgentState: ...

# Build graph
def create_agent_graph(llm: BaseChatModel, tools: list[BaseTool]):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("synthesize", synthesize_node)
    
    workflow.set_entry_point("plan")
    workflow.add_conditional_edges("plan", route_after_plan, {
        "execute": "execute",
        "synthesize": "synthesize",
    })
    workflow.add_edge("execute", "tools")
    workflow.add_edge("tools", "evaluate")
    workflow.add_conditional_edges("evaluate", route_after_evaluate, {
        "execute": "execute",
        "synthesize": "synthesize",
    })
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()
```

### Tool Definition
```python
from langchain_core.tools import tool

@tool
def search_knowledge_base(query: str, kb_id: str, top_k: int = 5) -> str:
    """Search a knowledge base. Use this to find relevant information."""
    # Implementation
    pass
```

### Key Rules
- Always set a max iteration limit (default: 10)
- Set a timeout for agent execution (default: 120s)
- Handle tool errors gracefully with retries
- Log every step for debugging and audit
- Stream intermediate steps for real-time UI
- Allow cancellation via run ID
- Validate tool inputs before execution
- Never execute arbitrary system commands without sandboxing
