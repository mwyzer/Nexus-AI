import json
import re

from ..config import settings
from ..core.llm import complete
from .state import AgentState
from .tools.base import ToolError
from .tools.defaults import default_tool_registry

PLAN_PROMPT = """Break the following task into a short, ordered list of concrete steps.
Reply with one step per line, no numbering, no extra commentary.

Task: {task}
"""

EXECUTE_PROMPT = """You are working on this overall task: {task}

Prior step results:
{prior_results}

Current step: {step}

Available tools:
{tools}

If a tool would help with this step, respond with exactly two lines:
TOOL: <tool_name>
ARGS: <a single-line JSON object of arguments>

Otherwise, respond with:
ANSWER: <a concise result for this step>
"""

_TOOL_DIRECTIVE_RE = re.compile(r"TOOL:\s*(\S+)\s*\n\s*ARGS:\s*(\{.*\})", re.DOTALL)

SYNTHESIZE_PROMPT = """Task: {task}

Step results:
{results}

Write a final answer to the task, using the step results above.
"""


def _parse_plan(raw: str) -> list[str]:
    steps = []
    for line in raw.splitlines():
        step = line.strip().lstrip("-*0123456789.) ").strip()
        if step:
            steps.append(step)
    return steps


def _parse_tool_directive(raw: str) -> tuple[str, dict] | None:
    """Parse a `TOOL: name` / `ARGS: {...}` directive out of a raw LLM response.

    Returns None (treat the whole response as a direct answer) if the response
    doesn't match the expected shape or ARGS isn't valid JSON -- the model
    producing free text instead of following the directive format shouldn't
    crash the run.
    """
    match = _TOOL_DIRECTIVE_RE.search(raw)
    if not match:
        return None
    name, args_json = match.groups()
    try:
        args = json.loads(args_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(args, dict):
        return None
    return name, args


def _strip_answer_prefix(raw: str) -> str:
    text = raw.strip()
    if text.upper().startswith("ANSWER:"):
        return text[len("ANSWER:") :].strip()
    return text


def _format_results(step_results: dict[int, str], plan: list[str]) -> str:
    if not step_results:
        return "(none yet)"
    return "\n".join(
        f"{i + 1}. {plan[i]} -> {step_results[i]}"
        for i in sorted(step_results)
        if i < len(plan)
    )


async def plan_node(state: AgentState) -> AgentState:
    raw = await complete(PLAN_PROMPT.format(task=state["task"]))
    plan = _parse_plan(raw)
    return {
        **state,
        "plan": plan,
        "current_step": 0,
        "step_results": {},
    }


async def execute_node(state: AgentState) -> AgentState:
    step_index = state["current_step"]
    step = state["plan"][step_index]
    prior_results = _format_results(state["step_results"], state["plan"])
    raw = await complete(
        EXECUTE_PROMPT.format(
            task=state["task"],
            prior_results=prior_results,
            step=step,
            tools=default_tool_registry.prompt_description(),
        )
    )

    directive = _parse_tool_directive(raw)
    if directive is None:
        result = _strip_answer_prefix(raw)
    else:
        tool_name, args = directive
        try:
            tool_result = await default_tool_registry.execute(tool_name, args)
            result = f"[{tool_name}] {tool_result}"
        except ToolError as exc:
            result = f"[{tool_name} error] {exc}"

    return {
        **state,
        "step_results": {**state["step_results"], step_index: result},
        "iteration_count": state["iteration_count"] + 1,
    }


async def evaluate_node(state: AgentState) -> AgentState:
    """Advance to the next step, or flag that the plan is exhausted."""
    next_step = state["current_step"] + 1
    return {**state, "current_step": next_step}


async def synthesize_node(state: AgentState) -> AgentState:
    results = _format_results(state["step_results"], state["plan"])
    answer = await complete(SYNTHESIZE_PROMPT.format(task=state["task"], results=results))
    return {**state, "final_output": answer}


def route_after_plan(state: AgentState) -> str:
    return "synthesize" if not state["plan"] else "execute"


def route_after_evaluate(state: AgentState) -> str:
    if state["iteration_count"] >= settings.agent_max_iterations:
        return "synthesize"
    if state["current_step"] >= len(state["plan"]):
        return "synthesize"
    return "execute"
