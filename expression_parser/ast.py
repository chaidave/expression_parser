"""
AST node definitions for a simple expression parser.
Tree structure representing parsed expressions.
"""

from abc import ABC, abstractmethod
from typing import Any, Union


class ASTNode(ABC):
    #Base class for all AST nodes.

    @abstractmethod
    def __repr__(self) -> str:
        pass


class ColumnRefNode(ASTNode):
    # Reference to DataFrame column. Evaluates to pd.Series.
    def __init__(self, column: str):
        self.column = column

    def __repr__(self) -> str:
        return f"ColumnRef({self.column!r})"


class LiteralNode(ASTNode):
    # Numeric constant value. Evaluates to scalar.
    def __init__(self, value: Union[int, float]):
        self.value = value

    def __repr__(self) -> str:
        return f"Literal({self.value!r})"


class BinaryOpNode(ASTNode):
    # Binary operation (e.g., +, -) between two sub-expressions.
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"BinaryOp({self.op!r}, {self.left!r}, {self.right!r})"


class FunctionNode(ASTNode):
    # Function call with single argument. (Placeholder - not yet implemented)
    def __init__(self, name: str, arg: ASTNode):
        self.name = name
        self.arg = arg

    def __repr__(self) -> str:
        return f"Function({self.name!r}, {self.arg!r})"
