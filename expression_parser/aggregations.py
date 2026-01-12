"""
This module provides functionality to apply aggregation functions to pandas Series
"""

import pandas as pd
from expression_parser.exceptions import UnsupportedAggregationError

# Registry pattern: maps function names to pandas aggregation methods
# To add new aggregation: add entry here (e.g., "max": "max")
AGGREGATION_FUNCTIONS = {
    "mean": "mean",
    "sum": "sum",
}


def apply_aggregation(df, series, group_by, aggregation):
    """
    Apply aggregation function to series grouped by a column.
    CRITICAL: Assumes series is pd.Series (not scalar). 
    Uses .iloc[:, 0] to extract aggregated column from result.
    """
    # Combine grouping column with series for aggregation
    temp_df = pd.concat([df[group_by], series], axis=1)

    func = aggregation["func"]
    agg_method = AGGREGATION_FUNCTIONS.get(func)

    if agg_method is None:
        raise UnsupportedAggregationError(func)

    # Apply aggregation and extract first column (the aggregated series)
    return getattr(temp_df.groupby(group_by), agg_method)().iloc[:, 0]
