"""
Exceptions for the expression parser module.
"""

class ExpressionParserError(Exception):
    """Base class for parser errors."""


class UnsupportedOperatorError(ExpressionParserError):
    def __init__(self, operator):
        super().__init__(f"Unsupported operator: {operator}")


class UnsupportedAggregationError(ExpressionParserError):
    def __init__(self, aggregation):
        super().__init__(f"Unsupported aggregation: {aggregation}")
