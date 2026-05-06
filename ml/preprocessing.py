from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


FEATURE_COLUMNS: Final[list[str]] = [
    "month",
    "quarter",
    "day_of_week",
    "is_weekend",
    "quantity",
    "price",
    "category_encoded",
    "customer_id",
    "product_id",
]
TARGET_COLUMN: Final[str] = "revenue"
CATEGORY_ALIASES: Final[tuple[str, ...]] = ("category", "product_category", "sub_category")
DATE_ALIASES: Final[tuple[str, ...]] = ("date", "order_date")
CUSTOMER_ALIASES: Final[tuple[str, ...]] = ("customer_id", "customer", "customer_name")
PRODUCT_ALIASES: Final[tuple[str, ...]] = ("product_id", "product", "product_name")
NUMERIC_FILL_COLUMNS: Final[list[str]] = [*FEATURE_COLUMNS]


@dataclass
class PreprocessingArtifacts:
    label_encoder: LabelEncoder
    customer_mapping: dict[str, int]
    product_mapping: dict[str, int]
    numeric_medians: dict[str, float]


def _normalize_text_series(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    return cleaned.replace({"": pd.NA, "<na>": pd.NA})


def _first_existing_column(df: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    for column_name in candidates:
        if column_name in df.columns:
            return column_name
    return None


def _coerce_numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    cleaned = series.astype("string").str.replace(",", "", regex=False)
    cleaned = cleaned.str.replace(r"[^\d.\-]", "", regex=True)
    cleaned = cleaned.replace({"": pd.NA, "-": pd.NA, ".": pd.NA, "-.": pd.NA})
    return pd.to_numeric(cleaned, errors="coerce")


def _coerce_datetime(series: pd.Series) -> pd.Series:
    parsed_default = pd.to_datetime(series, errors="coerce")
    parsed_dayfirst = pd.to_datetime(series, errors="coerce", dayfirst=True)
    if parsed_dayfirst.notna().sum() > parsed_default.notna().sum():
        return parsed_dayfirst
    return parsed_default


def _resolve_text_series(df: pd.DataFrame, aliases: tuple[str, ...], default_value: str = "unknown") -> pd.Series:
    column_name = _first_existing_column(df, aliases)
    if column_name is None:
        return pd.Series(default_value, index=df.index, dtype="string")
    return _normalize_text_series(df[column_name]).fillna(default_value)


def _default_numeric_series(df: pd.DataFrame, column_name: str) -> pd.Series:
    if column_name not in df.columns:
        return pd.Series(np.nan, index=df.index)
    return _coerce_numeric(df[column_name])


def _fit_mapping(series: pd.Series) -> dict[str, int]:
    normalized = _normalize_text_series(series).fillna("unknown").astype(str)
    unique_values = sorted(value for value in normalized.unique() if value and value != "unknown")
    return {value: index + 1 for index, value in enumerate(unique_values)}


def _map_with_default(series: pd.Series, mapping: dict[str, int], default_value: int = 0) -> pd.Series:
    normalized = _normalize_text_series(series).fillna("unknown").astype(str)
    return normalized.map(mapping).fillna(default_value).astype(int)


def _safe_label_encode(series: pd.Series, encoder: LabelEncoder) -> pd.Series:
    normalized = _normalize_text_series(series).fillna("unknown").astype(str)
    known_classes = {value: index for index, value in enumerate(encoder.classes_)}
    return normalized.map(known_classes).fillna(-1).astype(int)


def _resolve_target_series(df: pd.DataFrame, require_target: bool) -> pd.Series:
    if TARGET_COLUMN in df.columns:
        return _coerce_numeric(df[TARGET_COLUMN])
    if "sales" in df.columns:
        return _coerce_numeric(df["sales"])
    if require_target:
        raise ValueError(f"Missing target column: {TARGET_COLUMN}")
    return pd.Series(np.nan, index=df.index, dtype="float64")


def _resolve_date_series(df: pd.DataFrame) -> pd.Series:
    date_column = _first_existing_column(df, DATE_ALIASES)
    if date_column is not None:
        return _coerce_datetime(df[date_column])

    if {"year", "month"}.issubset(df.columns):
        year_series = _coerce_numeric(df["year"])
        month_series = _coerce_numeric(df["month"])
        return pd.to_datetime(
            pd.DataFrame({"year": year_series, "month": month_series, "day": 1}),
            errors="coerce",
        )

    return pd.Series(pd.NaT, index=df.index)


def _existing_feature_frame(df: pd.DataFrame, artifacts: PreprocessingArtifacts | None) -> pd.DataFrame | None:
    if not all(column_name in df.columns for column_name in FEATURE_COLUMNS):
        return None

    feature_frame = df[FEATURE_COLUMNS].copy()
    for column_name in FEATURE_COLUMNS:
        if column_name in {"customer_id", "product_id"} and not pd.api.types.is_numeric_dtype(feature_frame[column_name]):
            if artifacts is None:
                return None
            mapping = artifacts.customer_mapping if column_name == "customer_id" else artifacts.product_mapping
            feature_frame[column_name] = _map_with_default(feature_frame[column_name], mapping)
        else:
            feature_frame[column_name] = _coerce_numeric(feature_frame[column_name])

    return feature_frame


def _build_derived_feature_frame(df: pd.DataFrame, target: pd.Series, require_target: bool) -> pd.DataFrame:
    date_series = _resolve_date_series(df)
    month_series = _coerce_numeric(df["month"]) if "month" in df.columns else date_series.dt.month
    month_series = month_series.fillna(date_series.dt.month)

    if date_series.notna().any():
        day_of_week_series = date_series.dt.dayofweek.fillna(0).astype(int)
        is_weekend_series = (day_of_week_series >= 5).astype(int)
    else:
        day_of_week_series = _coerce_numeric(df["day_of_week"]) if "day_of_week" in df.columns else pd.Series(0, index=df.index)
        day_of_week_series = day_of_week_series.fillna(0).astype(int)
        if "is_weekend" in df.columns:
            is_weekend_series = _coerce_numeric(df["is_weekend"]).fillna(0).astype(int)
        else:
            is_weekend_series = (day_of_week_series >= 5).astype(int)

    quantity_series = _default_numeric_series(df, "quantity")
    price_series = _default_numeric_series(df, "price")

    category_source = _resolve_text_series(df, CATEGORY_ALIASES)
    customer_source = _resolve_text_series(df, CUSTOMER_ALIASES)
    product_source = _resolve_text_series(df, PRODUCT_ALIASES)

    quarter_series = ((month_series.fillna(1).astype(int) - 1) // 3 + 1).astype(int)
    revenue_per_unit_series = target / quantity_series.replace(0, pd.NA)

    feature_frame = pd.DataFrame(
        {
            "month": month_series,
            "quarter": quarter_series,
            "day_of_week": day_of_week_series,
            "is_weekend": is_weekend_series,
            "quantity": quantity_series,
            "price": price_series,
            "category": category_source,
            "customer_source": customer_source,
            "product_source": product_source,
            "revenue_per_unit": revenue_per_unit_series,
        }
    )

    valid_rows = pd.Series(True, index=df.index)
    if require_target:
        valid_rows &= target.notna()

    if feature_frame.empty:
        raise ValueError("No usable rows remain after preparing the ML feature frame.")

    return feature_frame.loc[valid_rows].reset_index(drop=True)


def _build_artifacts(
    category_source: pd.Series,
    customer_source: pd.Series,
    product_source: pd.Series,
) -> PreprocessingArtifacts:
    label_encoder = LabelEncoder()
    label_encoder.fit(_normalize_text_series(category_source).fillna("unknown").astype(str))
    return PreprocessingArtifacts(
        label_encoder=label_encoder,
        customer_mapping=_fit_mapping(customer_source),
        product_mapping=_fit_mapping(product_source),
        numeric_medians={},
    )


def _encode_identifier_columns(
    feature_frame: pd.DataFrame,
    artifacts: PreprocessingArtifacts,
) -> pd.DataFrame:
    encoded_frame = feature_frame.copy()
    category_source = encoded_frame.pop("category")
    customer_source = encoded_frame.pop("customer_source")
    product_source = encoded_frame.pop("product_source")

    encoded_frame["category_encoded"] = _safe_label_encode(category_source, artifacts.label_encoder)
    encoded_frame["customer_id"] = _map_with_default(customer_source, artifacts.customer_mapping)
    encoded_frame["product_id"] = _map_with_default(product_source, artifacts.product_mapping)
    return encoded_frame


def _ensure_numeric_medians(feature_frame: pd.DataFrame, artifacts: PreprocessingArtifacts) -> None:
    if artifacts.numeric_medians:
        return

    artifacts.numeric_medians = {
        column_name: float(feature_frame[column_name].median(skipna=True)) if feature_frame[column_name].notna().any() else 0.0
        for column_name in NUMERIC_FILL_COLUMNS
    }


def _fill_numeric_feature_columns(feature_frame: pd.DataFrame, artifacts: PreprocessingArtifacts) -> pd.DataFrame:
    filled_frame = feature_frame.copy()

    for column_name in FEATURE_COLUMNS:
        filled_frame[column_name] = pd.to_numeric(filled_frame[column_name], errors="coerce")
        filled_frame[column_name] = filled_frame[column_name].fillna(artifacts.numeric_medians.get(column_name, 0.0))

    filled_frame["revenue_per_unit"] = pd.to_numeric(filled_frame["revenue_per_unit"], errors="coerce")
    revenue_fill_value = float(filled_frame["revenue_per_unit"].median(skipna=True)) if filled_frame["revenue_per_unit"].notna().any() else 0.0
    filled_frame["revenue_per_unit"] = filled_frame["revenue_per_unit"].fillna(revenue_fill_value)
    return filled_frame


def _finalize_integer_feature_columns(feature_frame: pd.DataFrame) -> pd.DataFrame:
    finalized = feature_frame.copy()
    integer_columns = ("month", "quarter", "day_of_week", "is_weekend", "category_encoded", "customer_id", "product_id")

    for column_name in integer_columns:
        finalized[column_name] = finalized[column_name].round().astype(int)

    return finalized


def prepare_ml_dataset(
    df: pd.DataFrame,
    artifacts: PreprocessingArtifacts | None = None,
    fit_artifacts: bool = True,
    require_target: bool = True,
) -> tuple[pd.DataFrame, pd.Series | None, PreprocessingArtifacts]:
    """Build the Week 7 feature matrix and target vector."""
    target = _resolve_target_series(df, require_target=require_target)

    existing_feature_frame = _existing_feature_frame(df, artifacts if not fit_artifacts else None)
    if existing_feature_frame is not None:
        feature_frame = existing_feature_frame.copy()
    else:
        feature_frame = _build_derived_feature_frame(df, target, require_target=require_target)

    if existing_feature_frame is None:
        if artifacts is None or fit_artifacts:
            artifacts = _build_artifacts(
                category_source=feature_frame["category"],
                customer_source=feature_frame["customer_source"],
                product_source=feature_frame["product_source"],
            )

        feature_frame = _encode_identifier_columns(feature_frame, artifacts)

    feature_frame = feature_frame.reindex(columns=[*FEATURE_COLUMNS, "revenue_per_unit"])

    if "revenue_per_unit" not in feature_frame.columns:
        quantity_series = feature_frame["quantity"].replace(0, pd.NA)
        feature_frame["revenue_per_unit"] = target / quantity_series

    _ensure_numeric_medians(feature_frame, artifacts)
    feature_frame = _fill_numeric_feature_columns(feature_frame, artifacts)
    feature_frame = _finalize_integer_feature_columns(feature_frame)

    if target is not None:
        target = target.reset_index(drop=True)

    return feature_frame[FEATURE_COLUMNS], target, artifacts


def build_feature_target_frame(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, PreprocessingArtifacts]:
    """Compatibility wrapper for training."""
    feature_frame, target, artifacts = prepare_ml_dataset(df, require_target=True)
    if target is None:
        raise ValueError("Target column is required for training.")
    return feature_frame, target, artifacts


def prepare_prediction_frame(
    data: pd.DataFrame,
    artifacts: PreprocessingArtifacts,
) -> pd.DataFrame:
    """Transform new rows into the trained Week 7 feature layout."""
    feature_frame, _, _ = prepare_ml_dataset(data, artifacts=artifacts, fit_artifacts=False, require_target=False)
    return feature_frame


def build_preprocessor(scale_numeric: bool):
    """Retain a lightweight preprocessor for compatibility with older imports."""
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    numeric_steps: list[tuple[str, object]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    numeric_pipeline = Pipeline(numeric_steps)
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, FEATURE_COLUMNS),
        ]
    )
