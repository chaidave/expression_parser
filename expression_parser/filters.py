"""
Applies row-level filtering using comparison operators
"""

from expression_parser.exceptions import UnsupportedOperatorError

# Registry pattern: maps filter operators to comparison functions
# To add new operator: add entry here (e.g., ">=": lambda col, val: col >= val)
FILTER_OPERATORS = {
    ">": lambda col, val: col > val,
    "<": lambda col, val: col < val,
    "==": lambda col, val: col == val,
}


def apply_filters(df, filters):
    """
    Apply list of filter conditions sequentially to DataFrame.
    Each filter: {"column": str, "op": str, "value": any}
    Note: Preserves original DataFrame index after filtering.
    """
    for f in filters:
        col = f["column"]
        op = f["op"]
        val = f["value"]

        filter_func = FILTER_OPERATORS.get(op)
        if filter_func is None:
            raise UnsupportedOperatorError(op)

        df = df[filter_func(df[col], val)]

    return df
