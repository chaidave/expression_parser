"""
    Validates properties of a DataFrame.
"""

import pandas as pd

class DataFrameValidator:
    def __init__(self, required_columns = 4) -> None:
        self.required_columns = required_columns

    def validateDF(self, df) -> None:
        self._check_not_empty(df)
        self._check_column_count(df)

    def _check_not_empty(self, df) -> None:
        if df.empty:
            raise ValueError("DataFrame is empty")

    def _check_column_count(self, df) -> None:
        if df.shape[1] != self.required_columns:
            raise ValueError(
                f"DataFrame must have exactly {self.required_columns} columns, "
                f"found {df.shape[1]}"
            )


"""
This CSV validator module provides functionality to validate properties of a DataFrame.
This is valid for current use cases where we expect a DataFrame with exactly 4 columns.
But we cna easily extend this in the future for more complex validation rules as needed.
"""
