import asyncio

import pytest

from app.agents import nodes
from app.agents.runner import AgentCancelledError, run_agent


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    async def _fake_complete(prompt: str) -> str:
        if "Break the following task" in prompt:
            return "Research the topic\nWrite a summary"
        if "Write a final answer" in prompt:
            return "Final synthesized answer."
        return "step result"

    monkeypatch.setattr(nodes, "complete", _fake_complete)


async def test_run_agent_completes_full_plan():
    state = await run_agent("Summarize quarterly sales")

    assert state["plan"] == ["Research the topic", "Write a summary"]
    assert state["final_output"] == "Final synthesized answer."
    assert state["iteration_count"] == 2
    assert set(state["step_results"]) == {0, 1}
    assert state["step_results"][0] == "step result"


async def test_run_agent_with_empty_plan_skips_straight_to_synthesize(monkeypatch):
    async def _fake_complete(prompt: str) -> str:
        if "Break the following task" in prompt:
            return ""
        return "Final synthesized answer."

    monkeypatch.setattr(nodes, "complete", _fake_complete)

    state = await run_agent("A task with no discernible steps")

    assert state["plan"] == []
    assert state["iteration_count"] == 0
    assert state["final_output"] == "Final synthesized answer."


async def test_run_agent_stops_at_max_iterations(monkeypatch):
    monkeypatch.setattr(nodes.settings, "agent_max_iterations", 1)

    async def _fake_complete(prompt: str) -> str:
        if "Break the following task" in prompt:
            return "Step one\nStep two\nStep three"
        return "step result"

    monkeypatch.setattr(nodes, "complete", _fake_complete)

    state = await run_agent("A task with many steps")

    assert state["iteration_count"] == 1
    assert state["final_output"] is not None


async def test_run_agent_raises_on_cancellation(monkeypatch):
    cancel_event = asyncio.Event()
    cancel_event.set()

    with pytest.raises(AgentCancelledError):
        await run_agent("Any task", cancel_event=cancel_event)
