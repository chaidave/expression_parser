"""
This module provides functionality to parse and build an AST from expressions.
"""

from expression_parser.exceptions import UnsupportedOperatorError
from expression_parser.ast import ColumnRefNode, LiteralNode, BinaryOpNode

SUPPORTED_BINARY_OPS = {"+", "-"}


def parse_expression(expr):
    if isinstance(expr, str):
        return ColumnRefNode(expr)

    if isinstance(expr, (int, float)):
        return LiteralNode(expr)

    if isinstance(expr, dict):
        if "op" in expr:
            left = parse_expression(expr["left"])
            right = parse_expression(expr["right"])
            op = expr["op"]

            if op in SUPPORTED_BINARY_OPS:
                return BinaryOpNode(op, left, right)
            else:
                raise UnsupportedOperatorError(op)
        else:
            raise ValueError("Invalid expression format: dict must contain 'op'")

    raise ValueError("Invalid expression format")

