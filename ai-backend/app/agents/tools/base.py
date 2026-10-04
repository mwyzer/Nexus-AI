from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ValidationError


class ToolError(Exception):
    """Raised on bad arguments or a tool failure; caught by the registry, not the caller."""


class Tool(ABC):
    name: str
    description: str
    args_schema: type[BaseModel]

    async def __call__(self, raw_args: dict[str, Any]) -> str:
        try:
            args = self.args_schema(**raw_args)
        except ValidationError as exc:
            raise ToolError(f"Invalid arguments for tool '{self.name}': {exc}") from exc
        try:
            return await self.run(args)
        except ToolError:
            raise
        except Exception as exc:  # noqa: BLE001 - normalize unexpected tool failures for the agent
            raise ToolError(f"Tool '{self.name}' failed: {exc}") from exc

    @abstractmethod
    async def run(self, args: BaseModel) -> str:
        """Execute the tool and return a plain-text result for the agent to read."""

    def schema_description(self) -> str:
        """Human/LLM-readable one-liner describing the tool and its arguments, for prompting."""
        fields = self.args_schema.model_fields
        arg_descriptions = ", ".join(
            f"{name}: {getattr(field.annotation, '__name__', field.annotation)}"
            for name, field in fields.items()
        )
        return f"- {self.name}({arg_descriptions}): {self.description}"
