"""
    Validates properties of a DataFrame.
"""
import pandas as pd

class DataFrameValidator:
    def __init__(self):
        pass

    def validateDF(self, df) -> None:
        self._check_not_empty(df)

    def _check_not_empty(self, df) -> None:
        if df.empty:
            raise ValueError("DataFrame is empty")


"""
This CSV validator module provides functionality to validate properties of a DataFrame.
But we can easily extend this in the future for more complex validation rules such as checking and replacing missing values and NA.
"""
