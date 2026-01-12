"""
Evaluator for AST nodes and executes operations on DataFrames 
"""

import pandas as pd
from expression_parser.ast import ASTNode, ColumnRefNode, LiteralNode, BinaryOpNode, FunctionNode
from expression_parser.exceptions import UnsupportedOperatorError

# Registry pattern: maps operator symbols to functions
# To add new operator: add entry here (e.g., "*": lambda left, right: left * right)
BINARY_OPERATORS = {
    "+": lambda left, right: left + right,
    "-": lambda left, right: left - right,
}


def evaluate_ast(df: pd.DataFrame, node: ASTNode):
    """
    Recursively evaluate AST against DataFrame.
    NOTE: Returns pd.Series for columns, scalar for literals (mixed types).
    """
    if isinstance(node, ColumnRefNode):
        return df[node.column]

    elif isinstance(node, LiteralNode):
        # Returns scalar - validation prevents problematic combinations with aggregation
        return node.value

    elif isinstance(node, BinaryOpNode):
        # Recursively evaluate operands, then apply operation
        left = evaluate_ast(df, node.left)
        right = evaluate_ast(df, node.right)

        op_func = BINARY_OPERATORS.get(node.op)
        if op_func is None:
            raise UnsupportedOperatorError(node.op)
        return op_func(left, right)

    elif isinstance(node, FunctionNode):
        # Placeholder for future function support
        raise NotImplementedError(f"Function {node.name} not yet supported")

    else:
        raise ValueError(f"Unknown AST node type: {type(node)}")
