from expression_parser.exceptions import UnsupportedOperatorError

FILTER_OPERATORS = {
    ">": lambda col, val: col > val,
    "<": lambda col, val: col < val,
    "==": lambda col, val: col == val,
}


def apply_filters(df, filters):
    for f in filters:
        col = f["column"]
        op = f["op"]
        val = f["value"]

        filter_func = FILTER_OPERATORS.get(op)
        if filter_func is None:
            raise UnsupportedOperatorError(op)

        df = df[filter_func(df[col], val)]

    return df
