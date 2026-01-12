from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Literal, Tuple
import pandas as pd
import numpy as np


NumericStrategy = Literal["median", "mean", "constant"]
CategoricalStrategy = Literal["mode", "constant"]
DatetimeStrategy = Literal["mode", "constant", "skip"]


@dataclass(frozen=True)
class PreprocessConfig:
    # Duplicates
    drop_duplicates: bool = True
    duplicate_subset: Optional[list[str]] = None
    keep: Literal["first", "last", False] = "first"

    # Missing values
    numeric_strategy: NumericStrategy = "median"
    numeric_constant: float = 0.0

    categorical_strategy: CategoricalStrategy = "mode"
    categorical_constant: str = "unknown"

    datetime_strategy: DatetimeStrategy = "skip"
    datetime_constant: pd.Timestamp = pd.Timestamp("1970-01-01")

    # General
    treat_blank_strings_as_na: bool = True
    inplace: bool = False  # If True, modifies df in place


def clean_duplicates_and_missing(
    df: pd.DataFrame,
    config: PreprocessConfig = PreprocessConfig()
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    report: Dict[str, Any] = {}

    working_df = df if config.inplace else df.copy(deep=True)

    # 0) Normalize common missing markers
    if config.treat_blank_strings_as_na:
        # Convert empty/whitespace-only strings to NaN for object/string columns
        obj_cols = working_df.select_dtypes(include=["object", "string"]).columns
        if len(obj_cols) > 0:
            working_df[obj_cols] = working_df[obj_cols].replace(r"^\s*$", np.nan, regex=True)

    # 1) Duplicates
    dup_mask = working_df.duplicated(subset=config.duplicate_subset, keep=config.keep)
    dup_count = int(dup_mask.sum())
    report["duplicates_found"] = dup_count
    report["duplicates_subset"] = config.duplicate_subset
    report["duplicates_dropped"] = 0

    if config.drop_duplicates and dup_count > 0:
        before = len(working_df)
        working_df = working_df.drop_duplicates(
            subset=config.duplicate_subset,
            keep=config.keep
        )
        after = len(working_df)
        report["duplicates_dropped"] = before - after

    # 2) Missing values summary (before)
    missing_before = working_df.isna().sum()
    missing_before_pct = (missing_before / len(working_df) * 100).replace([np.inf, -np.inf], np.nan)
    report["missing_before"] = missing_before[missing_before > 0].to_dict()
    report["missing_before_pct"] = missing_before_pct[missing_before > 0].round(2).to_dict()

    # Helper imputers
    def fill_numeric(col: str) -> Any:
        s = working_df[col]
        if config.numeric_strategy == "median":
            val = s.median(skipna=True)
        elif config.numeric_strategy == "mean":
            val = s.mean(skipna=True)
        else:  # constant
            val = config.numeric_constant
        return val

    def fill_categorical(col: str) -> Any:
        s = working_df[col]
        if config.categorical_strategy == "mode":
            # mode() can return empty if all NaN
            mode_vals = s.mode(dropna=True)
            val = mode_vals.iloc[0] if len(mode_vals) > 0 else config.categorical_constant
        else:  # constant
            val = config.categorical_constant
        return val

    def fill_datetime(col: str) -> Optional[pd.Timestamp]:
        if config.datetime_strategy == "skip":
            return None
        s = working_df[col]
        if config.datetime_strategy == "mode":
            mode_vals = s.mode(dropna=True)
            return mode_vals.iloc[0] if len(mode_vals) > 0 else config.datetime_constant
        return config.datetime_constant

    # 3) Apply imputations by dtype
    imputed: Dict[str, Dict[str, Any]] = {"numeric": {}, "categorical": {}, "datetime": {}}

    # Numeric columns
    num_cols = working_df.select_dtypes(include=["number"]).columns
    for col in num_cols:
        na_count = int(working_df[col].isna().sum())
        if na_count == 0:
            continue
        val = fill_numeric(col)
        # If val is nan (e.g., entire column nan), fallback to constant
        if pd.isna(val):
            val = config.numeric_constant
        working_df[col] = working_df[col].fillna(val)
        imputed["numeric"][col] = {"filled_na": na_count, "value_used": val, "strategy": config.numeric_strategy}

    # Datetime columns
    dt_cols = working_df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns
    for col in dt_cols:
        na_count = int(working_df[col].isna().sum())
        if na_count == 0:
            continue
        val = fill_datetime(col)
        if val is None:
            continue
        working_df[col] = working_df[col].fillna(val)
        imputed["datetime"][col] = {"filled_na": na_count, "value_used": val, "strategy": config.datetime_strategy}

    # Categorical / string / object columns
    cat_cols = working_df.select_dtypes(include=["object", "string", "category", "bool"]).columns
    for col in cat_cols:
        na_count = int(working_df[col].isna().sum())
        if na_count == 0:
            continue
        val = fill_categorical(col)
        working_df[col] = working_df[col].fillna(val)
        imputed["categorical"][col] = {"filled_na": na_count, "value_used": val, "strategy": config.categorical_strategy}

    report["imputation"] = imputed

    # 4) Missing values summary (after)
    missing_after = working_df.isna().sum()
    report["missing_after"] = missing_after[missing_after > 0].to_dict()

    return working_df, report
