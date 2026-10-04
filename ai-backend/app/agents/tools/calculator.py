import ast
import operator

from pydantic import BaseModel, Field

from .base import Tool, ToolError

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
_UNARY_OPS = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval(node: ast.expr) -> float:
    """Evaluate a parsed arithmetic expression. Only numeric literals and +-*/%** are allowed."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval(node.operand))
    raise ValueError(f"Unsupported expression element: {ast.dump(node)}")


class CalculatorArgs(BaseModel):
    expression: str = Field(description="An arithmetic expression, e.g. '2 * (3 + 4)'")


class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluate a basic arithmetic expression (+ - * / % **)"
    args_schema = CalculatorArgs

    async def run(self, args: CalculatorArgs) -> str:
        try:
            tree = ast.parse(args.expression, mode="eval")
            result = _eval(tree.body)
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError) as exc:
            raise ToolError(f"Invalid expression {args.expression!r}: {exc}") from exc
        return str(result)
