from langgraph.graph import END, StateGraph

from .nodes import (
    evaluate_node,
    execute_node,
    plan_node,
    route_after_evaluate,
    route_after_plan,
    synthesize_node,
)
from .state import AgentState


def create_agent_graph():
    """Plan -> Execute -> Evaluate -> Synthesize, looping Execute/Evaluate per plan step.

    Tool calling (ToolNode) isn't wired in yet -- that's phase 3.2. Execute
    currently asks the LLM to produce each step's result directly.
    """
    workflow = StateGraph(AgentState)

    # Node id can't be "plan" -- LangGraph forbids a node name colliding
    # with a state key, and `plan` (the list[str] of steps) is a state key.
    workflow.add_node("planner", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("synthesize", synthesize_node)

    workflow.set_entry_point("planner")
    workflow.add_conditional_edges(
        "planner", route_after_plan, {"execute": "execute", "synthesize": "synthesize"}
    )
    workflow.add_edge("execute", "evaluate")
    workflow.add_conditional_edges(
        "evaluate", route_after_evaluate, {"execute": "execute", "synthesize": "synthesize"}
    )
    workflow.add_edge("synthesize", END)

    return workflow.compile()
