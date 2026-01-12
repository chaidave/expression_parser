from typing import Dict, Any, List

# Import registries to validate against supported operations
from expression_parser.expression_builder import SUPPORTED_BINARY_OPS
from expression_parser.filters import FILTER_OPERATORS
from expression_parser.aggregations import AGGREGATION_FUNCTIONS


class ConfigValidationError(Exception):
    pass


def validate_config(config: Dict[str, Any], df_columns: List[str]) -> None:
    # Check that config is not empty
    if not config:
        raise ConfigValidationError("Config cannot be empty")
    
    # Check required 'select' key
    if "select" not in config:
        raise ConfigValidationError("Config must contain 'select' key")

    # Validate select expression
    _validate_select_expression(config["select"], df_columns)

    # Validate optional filter
    if "filter" in config:
        _validate_filters(config["filter"], df_columns)

    # Validate aggregation requires group_by
    if "aggregate" in config:
        if "group_by" not in config:
            raise ConfigValidationError("Aggregation requires 'group_by' key")
        if config["group_by"] not in df_columns:
            raise ConfigValidationError(f"group_by column '{config['group_by']}' not found in DataFrame")
        _validate_aggregation(config["aggregate"])
    
    # Validate that group_by without aggregate is not allowed
    if "group_by" in config and "aggregate" not in config:
        raise ConfigValidationError("'group_by' specified but no 'aggregate' provided")
    
    # Check for unknown keys
    valid_keys = {"select", "filter", "group_by", "aggregate", "name"}
    unknown_keys = set(config.keys()) - valid_keys
    if unknown_keys:
        raise ConfigValidationError(f"Unknown config keys: {unknown_keys}")


def validate_plot_config(config: Dict[str, Any], df_columns: List[str]) -> None:
    # Check for simple format
    if "select" in config:
        # Validate that select is not a bare literal (meaningless for plotting)
        if isinstance(config["select"], (int, float)):
            raise ConfigValidationError(
                "Plotting a literal value (e.g., 42) is not meaningful. "
                "Use a column reference or expression instead."
            )
        # Validate the config
        validate_config(config, df_columns)
    
    # Check for plot format
    elif "x-values" in config and "y-values" in config:
        # Validate both x and y configs
        validate_config(config["x-values"], df_columns)
        validate_config(config["y-values"], df_columns)
        
        # Check for literals in x or y
        if isinstance(config["x-values"].get("select"), (int, float)):
            raise ConfigValidationError("x-values cannot be a literal value")
        if isinstance(config["y-values"].get("select"), (int, float)):
            raise ConfigValidationError("y-values cannot be a literal value")
    
    else:
        raise ConfigValidationError(
            "Config must have either 'select' or both 'x-values' and 'y-values'"
        )


def _validate_select_expression(expr: Any, df_columns: List[str]) -> None:
    if isinstance(expr, str):
        if expr not in df_columns:
            raise ConfigValidationError(f"Column '{expr}' not found in DataFrame")
    elif isinstance(expr, (int, float)):
        pass  # Literals are valid
    elif isinstance(expr, dict):
        if "op" not in expr:
            raise ConfigValidationError("Expression dict must contain 'op' key")
        if "left" not in expr or "right" not in expr:
            raise ConfigValidationError("Binary operation must have 'left' and 'right' keys")
        
        # Validate operator is supported
        op = expr["op"]
        if op not in SUPPORTED_BINARY_OPS:
            raise ConfigValidationError(
                f"Unsupported operator '{op}'. Supported operators: {sorted(SUPPORTED_BINARY_OPS)}"
            )
        
        # Recursively validate left and right
        _validate_select_expression(expr["left"], df_columns)
        _validate_select_expression(expr["right"], df_columns)
    else:
        raise ConfigValidationError(f"Invalid expression type: {type(expr).__name__}")


def _validate_filters(filters: List[Dict[str, Any]], df_columns: List[str]) -> None:
    if not isinstance(filters, list):
        raise ConfigValidationError("Filters must be a list")
    
    if len(filters) == 0:
        raise ConfigValidationError("Filter list cannot be empty")

    for idx, f in enumerate(filters):
        if not isinstance(f, dict):
            raise ConfigValidationError(f"Filter at index {idx} must be a dict")
        
        required_keys = {"column", "op", "value"}
        if not required_keys.issubset(f.keys()):
            missing = required_keys - set(f.keys())
            raise ConfigValidationError(f"Filter at index {idx} missing required keys: {missing}")
        
        # Validate column exists
        if f["column"] not in df_columns:
            raise ConfigValidationError(f"Filter column '{f['column']}' not found in DataFrame")
        
        # Validate operator is supported
        if f["op"] not in FILTER_OPERATORS:
            raise ConfigValidationError(
                f"Unsupported filter operator '{f['op']}'. Supported operators: {sorted(FILTER_OPERATORS.keys())}"
            )
        
        # Validate value type
        if not isinstance(f["value"], (int, float, str)):
            raise ConfigValidationError(
                f"Filter value must be int, float, or str, got {type(f['value']).__name__}"
            )


def _validate_aggregation(aggregation: Dict[str, Any]) -> None:
    if not isinstance(aggregation, dict):
        raise ConfigValidationError("Aggregation must be a dict")
    
    if "func" not in aggregation:
        raise ConfigValidationError("Aggregation must contain 'func' key")
    
    # Validate which aggregation function is supported
    func = aggregation["func"]
    if func not in AGGREGATION_FUNCTIONS:
        raise ConfigValidationError(
            f"Unsupported aggregation function '{func}'. Supported functions: {sorted(AGGREGATION_FUNCTIONS.keys())}"
        )
