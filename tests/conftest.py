import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "time": range(10),
        "param1": [0, 0, 1, 1, 2, 2, 0, 1, 2, 0],
        "param2": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "param3": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    })


@pytest.fixture
def empty_df():
    return pd.DataFrame(columns=["time", "param1", "param2", "param3"])
