import pandas as pd
from expression_parser.exceptions import UnsupportedAggregationError

# Registry of aggregation functions - maps func name to pandas agg method
AGGREGATION_FUNCTIONS = {
    "mean": "mean",
    "sum": "sum",
}


def apply_aggregation(df, series, group_by, aggregation):
    # Apply aggregation to a series grouped by a column.
    temp_df = pd.concat([df[group_by], series], axis=1)

    func = aggregation["func"]
    agg_method = AGGREGATION_FUNCTIONS.get(func)

    if agg_method is None:
        raise UnsupportedAggregationError(func)

    return getattr(temp_df.groupby(group_by), agg_method)().iloc[:, 0]
