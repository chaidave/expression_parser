"""
Main module - validates config, applies filters, evaluates expressions, and handles aggregations
"""

import pandas as pd
from expression_parser.filters import apply_filters
from expression_parser.expression_builder import parse_expression
from expression_parser.evaluator import evaluate_ast
from expression_parser.aggregations import apply_aggregation
from expression_parser.config_validator import validate_config, validate_plot_config, ConfigValidationError


class ExpressionParser:
    """
    Main entry point for expression evaluation.
    Takes JSON configs and evaluates them against a DataFrame.
    """
    def __init__(self, dataframe: pd.DataFrame):
        # Initialize with a DataFrame. Creates internal copy to avoid side effects.
        self.df = dataframe.copy()

    def evaluate(self, config: dict):
        """
        Evaluate expression config against DataFrame.
        Pipeline: validate -> filter -> parse -> evaluate -> aggregate
        Returns: pd.Series with computed results
        """
        # Validate config before processing
        validate_config(config, list(self.df.columns))

        df = self.df

        if "filter" in config:
            df = apply_filters(df, config["filter"])

        # Parse expression to AST, then evaluate
        ast_node = parse_expression(config["select"])
        series = evaluate_ast(df, ast_node)

        if "aggregate" in config:
            series = apply_aggregation(
                df=df,
                series=series,
                group_by=config["group_by"],
                aggregation=config["aggregate"]
            )

        return series

    def evaluate_plot_config(self, config: dict):
        """
        Evaluate config for plotting. Supports two formats:
        1. Simple: {"select": expr} -> generates indexed x-axis
        2. Plot: {"x-values": {...}, "y-values": {...}} -> explicit axes
        Returns: (x_series, y_series, x_label, y_label)
        """
        # Validate plot config (rejects bare literals)
        validate_plot_config(config, list(self.df.columns))
        
        # Apply top-level filter first if present
        df = self.df
        if "filter" in config:
            df = apply_filters(df, config["filter"])
        
        # Create a new parser with filtered data
        filtered_parser = ExpressionParser(df)
        
        # Support both config formats
        if "select" in config:
            # Simple format - use for tests and single-series plotting
            y = filtered_parser.evaluate(config)
            x = pd.Series(range(len(y)), name="index")
            x_name = "index"
            y_name = config.get("name", "value")
            
        elif "x-values" in config and "y-values" in config:
            # Plot format - use for x vs y plotting
            x = filtered_parser.evaluate(config["x-values"])
            y = filtered_parser.evaluate(config["y-values"])
            x_name = config["x-values"].get("name", "x-values")
            y_name = config["y-values"].get("name", "y-values")
            
        else:
            raise ConfigValidationError(
                "Config must have either 'select' or both 'x-values' and 'y-values'"
            )
        
        return x, y, x_name, y_name
