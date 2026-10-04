from .calculator import CalculatorTool
from .knowledge_base import KnowledgeBaseSearchTool
from .registry import ToolRegistry


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(KnowledgeBaseSearchTool())
    return registry


default_tool_registry = build_default_registry()
