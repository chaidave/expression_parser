# Expression Parser for Data Visualization

A flexible, config-driven expression parser for Pandas DataFrames. Define data transformations, filters, and aggregations using simple JSON configs.

---

## ⚙️  Setup Instructions

```bash

# Create a virtual environment and activate it

python -m venv venv
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install the package in editable mode (recommended)
pip install -e .

# Run demo with synthetic data
python demo/demo_plot.py

# Run with CSV file
python demo/demo_plot.py --data mydata.csv --config config/config.json

# Run tests
python -m pytest tests/
```

---

## 📁 Project Structure

```
expression_parser/
├── expression_parser/
│   ├── parser.py              # Main parser & orchestration
│   ├── expression_builder.py  # Parse JSON → AST
│   ├── evaluator.py           # Execute AST on DataFrames
│   ├── ast.py                 # AST node definitions
│   ├── filters.py             # Row filtering
│   ├── aggregations.py        # Group-by operations
│   ├── config_validator.py    # Config validation
│   └── exceptions.py          # Custom errors
├── config/
│   ├── config.json            # Plot config (x vs y)
│   └── sample_config.json     # Simple single-series config
├── demo/
│   └── demo_plot.py           # CLI demo with plotting
└── tests/
    └── test_parser.py         # Comprehensive test suite
```

---

## 🎯 Supported Operations

- ✅ **Config-driven** - Define queries in JSON
- ✅ **AST-based** - Clean separation of parsing & evaluation
- ✅ **Extensible** - Registry pattern for operators, filters, aggregations
- ✅ **Type-safe** - Comprehensive validation
- ✅ **Flexible data sources** - Synthetic, CSV, database (planned)
- ✅ **Two config formats** - Simple & plot formats

---

## 🖥️  CLI Usage

```bash
# Default (synthetic data + config/config.json)
python demo/demo_plot.py

# Specify data source
python demo/demo_plot.py --data synthetic
python demo/demo_plot.py --data mydata.csv

# Specify config
python demo/demo_plot.py --config config/simple_config.json

# Combine options
python demo/demo_plot.py --data sales.csv --config my_analysis.json
```

---

## 📊 Config Formats

### Simple Format
For single-series evaluation and testing:

```json
{
  "select": "param2",
  "filter": [
    { "column": "time", "op": ">", "value": 2 }
  ],
  "name": "result"
}
```

### Plot Format
For x vs y visualization:

```json
{
  "filter": [
    { "column": "time", "op": ">", "value": 2 }
  ],
  "x-values": {
    "select": "time"
  },
  "y-values": {
    "select": {
      "op": "+",
      "left": "param2",
      "right": "param3"
    },
    "name": "result"
  }
}
```

For more config review config directory

---

## 🔧 Supported Operations

### Operators
- `+` Addition
- `-` Subtraction

### Filters
- `>` Greater than
- `<` Less than
- `==` Equal to

### Aggregations
- `mean` Average by group
- `sum` Sum by group

### Expressions
- Column references: `"param2"`
- Literals: `42`, `3.14`
- Binary operations: `{"op": "+", "left": "param2", "right": "param3"}`

---

## 💻 Programmatic Usage

```python
import pandas as pd
from expression_parser.parser import ExpressionParser

# Load your data
df = pd.DataFrame({
    "time": range(10),
    "param1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "param2": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
})

# Create parser
parser = ExpressionParser(df)

# Simple evaluation
config = {"select": "param2"}
result = parser.evaluate(config)

# Plot evaluation (returns x, y, x_name, y_name)
plot_config = {
    "x-values": {"select": "time"},
    "y-values": {"select": "param2"}
}
x, y, x_name, y_name = parser.evaluate_plot_config(plot_config)
```

---

## 🔧 Extending Functionality

The codebase uses a **registry pattern** that makes it easy to add new operations without modifying core logic.

### Adding New Binary Operators

**Example: Add multiplication (`*`) operator**

1. **Update `expression_builder.py`:**
```python
# Add to SUPPORTED_BINARY_OPS set
SUPPORTED_BINARY_OPS = {"+", "-", "*"}
```

2. **Update `evaluator.py`:**
```python
# Add to BINARY_OPERATORS dict
BINARY_OPERATORS = {
    "+": lambda left, right: left + right,
    "-": lambda left, right: left - right,
    "*": lambda left, right: left * right,
}
```

**That's it!** Now you can use multiplication in configs:
```json
{
  "select": {
    "op": "*",
    "left": "param2",
    "right": "param3"
  }
}
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_parser.py::TestExpressionParser::test_column_selection -v

# Run with coverage
python -m pytest tests/ --cov=expression_parser
```

---

## 🎨 Design Principles

1. **Separation of Concerns** - Parsing ≠ Evaluation
2. **Single Responsibility** - Each module does one thing
3. **Open/Closed** - Open for extension, closed for modification
4. **Registry Pattern** - Easy to add new operations
5. **Type Safety** - Validation before execution
6. **Clean API** - Simple interface, complex internals

---
