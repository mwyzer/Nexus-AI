import logging
import time

from .base import Tool, ToolError

logger = logging.getLogger("agent.tools")


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def prompt_description(self) -> str:
        if not self._tools:
            return "(no tools available)"
        return "\n".join(t.schema_description() for t in self._tools.values())

    async def execute(self, name: str, raw_args: dict) -> str:
        tool = self.get(name)
        if tool is None:
            raise ToolError(f"Unknown tool: {name}")

        started = time.monotonic()
        try:
            result = await tool(raw_args)
            logger.info(
                "tool=%s args=%s duration_ms=%.1f status=ok",
                name, raw_args, (time.monotonic() - started) * 1000,
            )
            return result
        except ToolError as exc:
            logger.warning(
                "tool=%s args=%s duration_ms=%.1f status=error error=%s",
                name, raw_args, (time.monotonic() - started) * 1000, exc,
            )
            raise
