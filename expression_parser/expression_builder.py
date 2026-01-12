"""
This module provides functionality to parse and build an AST from expressions.
Converts JSON configs to AST node tree structure.
"""

from expression_parser.exceptions import UnsupportedOperatorError
from expression_parser.ast import ColumnRefNode, LiteralNode, BinaryOpNode

# Registry pattern: add supported operators here
SUPPORTED_BINARY_OPS = {"+", "-"}


def parse_expression(expr):
    """
    Parse JSON expression into AST nodes.
    - String -> ColumnRefNode (e.g., "temperature")
    - Number -> LiteralNode (e.g., 42)
    - Dict with "op" -> BinaryOpNode (e.g., {"op": "+", "left": "a", "right": "b"})
    """
    if isinstance(expr, str):
        return ColumnRefNode(expr)

    if isinstance(expr, (int, float)):
        return LiteralNode(expr)

    if isinstance(expr, dict):
        if "op" in expr:
            # Recursively parse left and right operands
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

