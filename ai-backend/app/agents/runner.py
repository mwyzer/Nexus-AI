import asyncio
import time
from collections.abc import AsyncIterator

from ..config import settings
from .graph import create_agent_graph
from .state import AgentState


class AgentCancelledError(Exception):
    pass


class AgentTimeoutError(Exception):
    pass


_graph = create_agent_graph()


def _initial_state(task: str) -> AgentState:
    return {
        "task": task,
        "plan": [],
        "current_step": 0,
        "iteration_count": 0,
        "step_results": {},
        "final_output": None,
        "error": None,
    }


async def stream_agent(
    task: str,
    cancel_event: asyncio.Event | None = None,
    timeout: float | None = None,
) -> AsyncIterator[AgentState]:
    """Run the agent graph, yielding the state after each node.

    LangGraph's own invocation doesn't take a cancel token or a wall-clock
    timeout, so both are enforced here, between steps, using `.astream()`
    (which also doubles as the streaming support the step UI needs).
    """
    deadline = time.monotonic() + (
        timeout if timeout is not None else settings.agent_timeout_seconds
    )
    state = _initial_state(task)
    yield state

    async for update in _graph.astream(state):
        if cancel_event is not None and cancel_event.is_set():
            raise AgentCancelledError(f"Agent run cancelled for task: {task!r}")
        if time.monotonic() > deadline:
            raise AgentTimeoutError(f"Agent run exceeded timeout for task: {task!r}")

        if "task" in update:
            # "values" stream mode: `update` is already the full merged state.
            state = {**state, **update}
        else:
            # "updates" stream mode: {node_name: partial_state}. Note "task"
            # can never collide with a node name, so this check is reliable
            # even though a node happens to be named "plan" (a state field too).
            for node_output in update.values():
                state = {**state, **node_output}
        yield state


async def run_agent(
    task: str,
    cancel_event: asyncio.Event | None = None,
    timeout: float | None = None,
) -> AgentState:
    """Run the agent graph to completion and return the final state."""
    final_state: AgentState | None = None
    async for state in stream_agent(task, cancel_event=cancel_event, timeout=timeout):
        final_state = state
    assert final_state is not None
    return final_state
