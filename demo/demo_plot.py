import json
import argparse
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from expression_parser.parser import ExpressionParser
from expression_parser.csv_validator import DataFrameValidator

def load_synthetic_data():
    df = pd.DataFrame({
        "time": range(0, 50),
        "param1": np.random.randint(0, 10, 50),
        "param2": np.random.randint(0, 9, 50),
        "param3": np.random.uniform(0, 1, 50),
    })
    print("Loaded synthetic data:")
    print(df.head(5))
    return df


def load_csv_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded data from CSV: {csv_path}")
        csvValidator = DataFrameValidator()
        csvValidator.validateDF(df)
        print(df.head(5))
        return df
    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

def create_argument_parser():
    parser = argparse.ArgumentParser(
        description="Expression Parser Demo - Plot data using JSON config",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use synthetic data with default config
  python demo_plot.py --data synthetic
  
  # Use CSV with custom config
  python demo_plot.py --data data.csv --config my_config.json
  
  # Use simple test config format
  python demo_plot.py --config config/simple_config.json
        """
    )
    
    parser.add_argument(
        "--data", type=str,default="synthetic",
        help='Data source: "synthetic", "database", or path to CSV file (default: synthetic)'
    )
    
    parser.add_argument(
        "--config", type=str, default="config/config.json",
        help="Path to JSON config file (default: config/config.json)"
    )
    
    return parser

def load_data(data_arg):
    if data_arg == "synthetic":
        return load_synthetic_data()
    elif data_arg == "database":
        print("Database support - placeholder for future implementation.")
        sys.exit(0)
    else:
        # Treat as CSV file path
        return load_csv_data(data_arg)


def main():
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Load data
    df = load_data(args.data)
    
    # Load config
    BASE_DIR = Path(__file__).resolve().parent.parent
    config_path = BASE_DIR / args.config if not Path(args.config).is_absolute() else Path(args.config)
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        print(f"\nUsing config: {config_path}")
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON config: {e}")
        sys.exit(1)
    
    expr_parser = ExpressionParser(df)
    
    # Support multiple plots if "plots" key exists
    if "plots" in config:
        num_plots = len(config["plots"])
        fig, axes = plt.subplots(1, num_plots, figsize=(6*num_plots, 5))
        if num_plots == 1:
            axes = [axes]
        
        for idx, plot_cfg in enumerate(config["plots"]):
            x, y, x_name, y_name = expr_parser.evaluate_plot_config(plot_cfg)
            axes[idx].plot(x.values, y.values, marker="o")
            axes[idx].set_xlabel(x_name)
            axes[idx].set_ylabel(y_name)
            axes[idx].set_title(plot_cfg.get("title", f"Plot {idx+1}"))
            axes[idx].grid(True, alpha=0.3)
        plt.tight_layout()
    else:
        # Single plot
        x, y, x_name, y_name = expr_parser.evaluate_plot_config(config)
        plt.plot(x.values, y.values, marker="o")
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        plt.title("Expression Parser Demo")
        plt.grid(True, alpha=0.3)
    
    plt.show()


if __name__ == "__main__":
    main()
