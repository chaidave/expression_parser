import pandas as pd
from expression_parser.ast import ASTNode, ColumnRefNode, LiteralNode, BinaryOpNode, FunctionNode
from expression_parser.exceptions import UnsupportedOperatorError

# Registry of binary operators - maps op to function
BINARY_OPERATORS = {
    "+": lambda left, right: left + right,
    "-": lambda left, right: left - right,
}


def evaluate_ast(df: pd.DataFrame, node: ASTNode):
    if isinstance(node, ColumnRefNode):
        return df[node.column]

    elif isinstance(node, LiteralNode):
        return node.value

    elif isinstance(node, BinaryOpNode):
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
