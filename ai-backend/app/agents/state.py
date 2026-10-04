from typing import TypedDict


class AgentState(TypedDict):
    """State threaded through the Plan -> Execute -> Evaluate -> Synthesize graph."""

    task: str
    plan: list[str]
    current_step: int
    iteration_count: int
    step_results: dict[int, str]
    final_output: str | None
    error: str | None
