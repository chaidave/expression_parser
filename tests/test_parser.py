import pytest
import pandas as pd
from expression_parser.parser import ExpressionParser
from expression_parser.config_validator import ConfigValidationError


class TestExpressionParser:

    def test_column_selection(self, sample_df):
        config = {"select": "param2"}
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        pd.testing.assert_series_equal(result, sample_df["param2"])

    def test_literal_value(self, sample_df):
        config = {"select": 42}
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        # Literal returns a scalar, not a Series
        assert result == 42

    def test_binary_addition(self, sample_df):
        config = {"select": {"op": "+", "left": "param2", "right": "param3"}}
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        expected = sample_df["param2"] + sample_df["param3"]
        pd.testing.assert_series_equal(result, expected)

    def test_binary_subtraction(self, sample_df):
        config = {"select": {"op": "-", "left": "param2", "right": "param3"}}
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        expected = sample_df["param2"] - sample_df["param3"]
        pd.testing.assert_series_equal(result, expected)

    def test_filters_single(self, sample_df):
        config = {
            "select": "param2",
            "filter": [{"column": "time", "op": ">", "value": 5}]
        }
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        expected_df = sample_df[sample_df["time"] > 5]
        pd.testing.assert_series_equal(result, expected_df["param2"])

    def test_filters_multiple(self, sample_df):
        config = {
            "select": "param2",
            "filter": [
                {"column": "time", "op": ">", "value": 3},
                {"column": "param1", "op": "==", "value": 2}
            ]
        }
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        expected_df = sample_df[(sample_df["time"] > 3) & (sample_df["param1"] == 2)]
        pd.testing.assert_series_equal(result, expected_df["param2"])

    def test_aggregation_mean(self, sample_df):
        config = {
            "select": "param2",
            "group_by": "param1",
            "aggregate": {"func": "mean"}
        }
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        expected = sample_df.groupby("param1")["param2"].mean()
        pd.testing.assert_series_equal(result, expected)

    def test_aggregation_sum(self, sample_df):
        config = {
            "select": "param2",
            "group_by": "param1",
            "aggregate": {"func": "sum"}
        }
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        expected = sample_df.groupby("param1")["param2"].sum()
        pd.testing.assert_series_equal(result, expected)

    def test_full_pipeline(self, sample_df):
        config = {
            "select": {"op": "+", "left": "param2", "right": "param3"},
            "filter": [{"column": "time", "op": ">", "value": 2}],
            "group_by": "param1",
            "aggregate": {"func": "mean"}
        }
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        filtered_df = sample_df[sample_df["time"] > 2]
        computed = filtered_df["param2"] + filtered_df["param3"]
        # Create temp dataframe to match aggregation logic
        temp_df = pd.concat([filtered_df["param1"], computed], axis=1)
        expected = temp_df.groupby("param1").mean().iloc[:, 0]
        pd.testing.assert_series_equal(result, expected)

    def test_invalid_column(self, sample_df):
        config = {"select": "nonexistent"}
        parser = ExpressionParser(sample_df)
        with pytest.raises(ConfigValidationError):
            parser.evaluate(config)

    def test_missing_select(self, sample_df):
        config = {"filter": [{"column": "time", "op": ">", "value": 5}]}
        parser = ExpressionParser(sample_df)
        with pytest.raises(ConfigValidationError):
            parser.evaluate(config)

    def test_aggregation_without_group_by(self, sample_df):
        config = {
            "select": "param2",
            "aggregate": {"func": "mean"}
        }
        parser = ExpressionParser(sample_df)
        with pytest.raises(ConfigValidationError):
            parser.evaluate(config)

    def test_invalid_operator(self, sample_df):
        config = {"select": {"op": "*", "left": "param2", "right": "param3"}}
        parser = ExpressionParser(sample_df)
        with pytest.raises(Exception):  # UnsupportedOperatorError from parsing
            parser.evaluate(config)

    def test_empty_dataframe_after_filter(self, sample_df):
        config = {
            "select": "param2",
            "filter": [{"column": "time", "op": ">", "value": 100}]
        }
        parser = ExpressionParser(sample_df)
        result = parser.evaluate(config)
        assert len(result) == 0
        assert result.dtype == sample_df["param2"].dtype
