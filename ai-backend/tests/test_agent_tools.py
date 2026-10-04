import pytest

from app.agents import nodes
from app.agents.runner import run_agent
from app.agents.tools.base import ToolError
from app.agents.tools.calculator import CalculatorTool
from app.agents.tools.registry import ToolRegistry


async def test_calculator_tool_evaluates_arithmetic():
    tool = CalculatorTool()
    assert await tool({"expression": "2 * (3 + 4)"}) == "14"
    assert await tool({"expression": "-5 + 1"}) == "-4"


async def test_calculator_tool_rejects_non_arithmetic():
    tool = CalculatorTool()
    with pytest.raises(ToolError):
        await tool({"expression": "__import__('os').system('echo pwned')"})


async def test_calculator_tool_rejects_invalid_args():
    tool = CalculatorTool()
    with pytest.raises(ToolError):
        await tool({})  # missing required "expression"


async def test_registry_raises_on_unknown_tool():
    registry = ToolRegistry()
    with pytest.raises(ToolError):
        await registry.execute("does_not_exist", {})


async def test_registry_executes_registered_tool():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    result = await registry.execute("calculator", {"expression": "1 + 1"})
    assert result == "2"


def test_parse_tool_directive_extracts_name_and_args():
    raw = 'TOOL: calculator\nARGS: {"expression": "2 + 2"}'
    assert nodes._parse_tool_directive(raw) == ("calculator", {"expression": "2 + 2"})


def test_parse_tool_directive_returns_none_for_plain_text():
    assert nodes._parse_tool_directive("ANSWER: just a plain answer") is None


def test_parse_tool_directive_returns_none_for_malformed_json():
    raw = "TOOL: calculator\nARGS: {not valid json}"
    assert nodes._parse_tool_directive(raw) is None


async def test_execute_node_invokes_tool_via_directive(monkeypatch):
    async def _fake_complete(prompt: str) -> str:
        if "Break the following task" in prompt:
            return "Compute 6 times 7"
        if "Write a final answer" in prompt:
            return "The answer is 42."
        return 'TOOL: calculator\nARGS: {"expression": "6 * 7"}'

    monkeypatch.setattr(nodes, "complete", _fake_complete)

    state = await run_agent("What is 6 times 7?")

    assert state["step_results"][0] == "[calculator] 42"
    assert state["final_output"] == "The answer is 42."


async def test_execute_node_surfaces_tool_error_without_crashing(monkeypatch):
    async def _fake_complete(prompt: str) -> str:
        if "Break the following task" in prompt:
            return "Compute something invalid"
        if "Write a final answer" in prompt:
            return "Could not compute."
        return 'TOOL: calculator\nARGS: {"expression": "1 / 0"}'

    monkeypatch.setattr(nodes, "complete", _fake_complete)

    state = await run_agent("Divide by zero")

    assert state["step_results"][0].startswith("[calculator error]")
    assert state["final_output"] == "Could not compute."
