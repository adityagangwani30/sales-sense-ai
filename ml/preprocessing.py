from __future__ import annotations

from typing import Final

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


FEATURE_COLUMNS: Final[list[str]] = ["month", "quantity", "price", "category", "region"]
TARGET_COLUMN: Final[str] = "sales"
CATEGORY_ALIASES: Final[tuple[str, ...]] = ("category", "product_category", "sub_category")
REGION_ALIASES: Final[tuple[str, ...]] = ("region",)
NUMERIC_FEATURES: Final[list[str]] = ["month", "quantity", "price"]
CATEGORICAL_FEATURES: Final[list[str]] = ["category", "region"]


def _normalize_text_series(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    return cleaned.replace({"": pd.NA})


def _resolve_feature_series(df: pd.DataFrame, aliases: tuple[str, ...]) -> pd.Series | None:
    for column_name in aliases:
        if column_name in df.columns:
            return df[column_name]
    return None


def build_feature_target_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return the exact Week 6 feature matrix and target vector."""
    source = df.copy()

    if TARGET_COLUMN not in source.columns:
        raise ValueError(f"Missing target column: {TARGET_COLUMN}")

    month_series = pd.to_numeric(source["month"], errors="coerce") if "month" in source.columns else pd.Series(pd.NA, index=source.index)
    if month_series.isna().all() and "date" in source.columns:
        month_series = pd.to_datetime(source["date"], errors="coerce").dt.month

    quantity_series = pd.to_numeric(source["quantity"], errors="coerce") if "quantity" in source.columns else pd.Series(pd.NA, index=source.index)
    price_series = pd.to_numeric(source["price"], errors="coerce") if "price" in source.columns else pd.Series(pd.NA, index=source.index)

    category_series = _resolve_feature_series(source, CATEGORY_ALIASES)
    if category_series is None:
        raise ValueError("Missing categorical feature: category")

    region_series = _resolve_feature_series(source, REGION_ALIASES)
    if region_series is None:
        raise ValueError("Missing categorical feature: region")

    target = pd.to_numeric(source[TARGET_COLUMN], errors="coerce")

    feature_frame = pd.DataFrame(
        {
            "month": month_series,
            "quantity": quantity_series,
            "price": price_series,
            "category": _normalize_text_series(category_series).fillna("unknown"),
            "region": _normalize_text_series(region_series).fillna("unknown"),
        }
    )

    valid_rows = target.notna()
    for column_name in ("month", "quantity", "price"):
        valid_rows &= feature_frame[column_name].notna()

    feature_frame = feature_frame.loc[valid_rows].reset_index(drop=True)
    target = target.loc[valid_rows].reset_index(drop=True)

    if feature_frame.empty:
        raise ValueError("No usable rows remain after preparing the Week 6 features.")

    return feature_frame, target


def build_preprocessor(scale_numeric: bool) -> ColumnTransformer:
    """Create the shared preprocessing pipeline for the regression models."""
    numeric_steps: list[tuple[str, object]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    numeric_pipeline = Pipeline(numeric_steps)
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )
