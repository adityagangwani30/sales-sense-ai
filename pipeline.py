from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Mapping, Sequence

import pandas as pd

from database_loader import load_cleaned_data_to_mysql


DATA_DIR = Path("original_dataset")
OUTPUT_DIR = Path("outputs")
DATASET_FILES: Dict[str, Path] = {
    "global_ecommerce_sales": DATA_DIR / "global_ecommerce_sales.csv",
    "retail_supply_chain_sales": DATA_DIR / "Retail-Supply-Chain-Sales-Dataset.xlsx",
}

DEFAULT_COLUMN_MAP: Dict[str, list[str]] = {
    "date": ["order_date", "order date", "date"],
    "sales": ["total_sales", "total sales", "sales", "revenue"],
    "product": ["product_name", "product name", "product"],
    "customer": ["customer_name", "customer name", "customer"],
    "quantity": ["quantity", "qty"],
    "price": ["unit_price", "unit price", "price"],
}

REQUIRED_COLUMNS: tuple[str, ...] = ("date", "sales")
NUMERIC_COLUMNS: tuple[str, ...] = ("sales", "price", "quantity")


def normalize_column_name(column_name: str) -> str:
    """Convert a raw column name into a simple lowercase format."""
    column_name = str(column_name).strip().lower()
    column_name = re.sub(r"[^a-z0-9]+", "_", column_name)
    return column_name.strip("_")


def get_dataset_path(dataset_choice: str | None = None) -> tuple[str, Path]:
    """Resolve the user's dataset choice to one file inside original_dataset."""
    dataset_aliases = {
        "1": "global_ecommerce_sales",
        "2": "retail_supply_chain_sales",
        "global_ecommerce_sales.csv": "global_ecommerce_sales",
        "retail-supply-chain-sales-dataset.xlsx": "retail_supply_chain_sales",
        "retail_supply_chain_sales.xlsx": "retail_supply_chain_sales",
    }

    if dataset_choice is None:
        print("Available datasets:")
        print("  1. global_ecommerce_sales")
        print("  2. retail_supply_chain_sales")
        dataset_choice = input("Enter dataset name or number: ").strip()

    normalized_choice = dataset_choice.strip().lower()
    dataset_name = dataset_aliases.get(normalized_choice, normalized_choice)

    if dataset_name not in DATASET_FILES:
        valid_choices = ", ".join(DATASET_FILES.keys())
        raise ValueError(f"Invalid dataset choice. Choose one of: {valid_choices}")

    dataset_path = DATASET_FILES[dataset_name]
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    return dataset_name, dataset_path


def load_data(dataset_choice: str | None = None) -> tuple[str, pd.DataFrame]:
    """Load only the dataset selected by the user."""
    dataset_name, dataset_path = get_dataset_path(dataset_choice)

    if dataset_path.suffix.lower() == ".csv":
        dataset = pd.read_csv(dataset_path)
    else:
        dataset = pd.read_excel(dataset_path)

    print(f"Selected dataset: {dataset_name}")
    print(f"Source file: {dataset_path}")
    print(f"Original shape: {dataset.shape}")

    return dataset_name, dataset


def detect_columns(
    df: pd.DataFrame,
    column_map: Mapping[str, Sequence[str]],
) -> Dict[str, str]:
    """Match dataset columns to the standard SalesSense column names."""
    detected_columns: Dict[str, str] = {}

    for standard_name, aliases in column_map.items():
        candidates = [standard_name, *aliases]
        for candidate in candidates:
            normalized_candidate = normalize_column_name(candidate)
            if normalized_candidate in df.columns:
                detected_columns[standard_name] = normalized_candidate
                break

    return detected_columns


def coalesce_standard_columns(
    df: pd.DataFrame,
    detected_columns: Mapping[str, str],
) -> pd.DataFrame:
    """Rename detected columns to the standard schema."""
    standardized = df.copy()

    for standard_name, detected_name in detected_columns.items():
        if detected_name == standard_name:
            continue
        standardized = standardized.rename(columns={detected_name: standard_name})

    return standardized.loc[:, ~standardized.columns.duplicated()]


def parse_date_series(series: pd.Series) -> pd.Series:
    """Parse date values and keep the version with more valid rows."""
    parsed_default = pd.to_datetime(series, errors="coerce")
    parsed_dayfirst = pd.to_datetime(series, errors="coerce", dayfirst=True)

    if parsed_dayfirst.notna().sum() > parsed_default.notna().sum():
        return parsed_dayfirst
    return parsed_default


def to_numeric_series(series: pd.Series) -> pd.Series:
    """Convert text-like numeric values into real numbers."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.str.replace(",", "", regex=False)
    cleaned = cleaned.str.replace(r"[^\d.\-]", "", regex=True)
    cleaned = cleaned.replace({"": pd.NA, "-": pd.NA, ".": pd.NA, "-.": pd.NA})
    return pd.to_numeric(cleaned, errors="coerce")


def fill_missing_numeric_values(
    df: pd.DataFrame,
    numeric_columns: Sequence[str],
) -> pd.DataFrame:
    """Fill missing numeric values using the median of each column."""
    completed = df.copy()

    for column_name in numeric_columns:
        if column_name not in completed.columns:
            continue
        median_value = completed[column_name].median(skipna=True)
        if pd.notna(median_value):
            completed[column_name] = completed[column_name].fillna(median_value)

    return completed


def clean_data(
    df: pd.DataFrame,
    column_map: Mapping[str, Sequence[str]],
    required_columns: Sequence[str],
    numeric_columns: Sequence[str],
) -> tuple[pd.DataFrame, Dict[str, str]]:
    """Standardize column names, improve data quality, and prepare the dataset."""
    cleaned = df.copy()
    cleaned.columns = [normalize_column_name(column_name) for column_name in cleaned.columns]
    cleaned = cleaned.loc[:, ~cleaned.columns.duplicated()]

    detected_columns = detect_columns(cleaned, column_map)
    cleaned = coalesce_standard_columns(cleaned, detected_columns)

    missing_required = [column_name for column_name in required_columns if column_name not in cleaned.columns]
    if missing_required:
        available_columns = ", ".join(cleaned.columns)
        raise ValueError(
            "Missing required columns after mapping: "
            f"{', '.join(missing_required)}. Available columns: {available_columns}"
        )

    for column_name in cleaned.select_dtypes(include=["object", "string"]).columns:
        cleaned[column_name] = cleaned[column_name].astype("string")
        cleaned[column_name] = cleaned[column_name].str.lower()
        cleaned[column_name] = cleaned[column_name].str.replace(r"\s+", " ", regex=True).str.strip()
        cleaned[column_name] = cleaned[column_name].replace({"": pd.NA})

    cleaned["date"] = parse_date_series(cleaned["date"])

    for column_name in numeric_columns:
        if column_name in cleaned.columns:
            cleaned[column_name] = to_numeric_series(cleaned[column_name])

    if "sales" not in cleaned.columns and {"price", "quantity"}.issubset(cleaned.columns):
        cleaned["sales"] = cleaned["price"] * cleaned["quantity"]
        detected_columns = dict(detected_columns)
        detected_columns["sales"] = "derived_from_price_quantity"

    if "price" not in cleaned.columns and {"sales", "quantity"}.issubset(cleaned.columns):
        cleaned["price"] = cleaned["sales"] / cleaned["quantity"].replace(0, pd.NA)
        detected_columns = dict(detected_columns)
        detected_columns["price"] = "derived_from_sales_quantity"

    if {"sales", "price", "quantity"}.issubset(cleaned.columns):
        cleaned["sales"] = cleaned["sales"].fillna(cleaned["price"] * cleaned["quantity"])
        derived_price = cleaned["sales"] / cleaned["quantity"].replace(0, pd.NA)
        cleaned["price"] = cleaned["price"].fillna(derived_price)

    for column_name in ("customer", "product"):
        if column_name not in cleaned.columns:
            cleaned[column_name] = "unknown"

    duplicate_subset = [column_name for column_name in ["date", "product", "customer"] if column_name in cleaned.columns]
    duplicate_count = int(cleaned.duplicated(subset=duplicate_subset).sum()) if duplicate_subset else 0
    if duplicate_subset:
        cleaned = cleaned.drop_duplicates(subset=duplicate_subset).reset_index(drop=True)

    missing_before_fill = cleaned.isna().sum()

    cleaned = fill_missing_numeric_values(cleaned, numeric_columns)

    for column_name in cleaned.select_dtypes(include=["object", "string"]).columns:
        if column_name in cleaned.columns:
            cleaned[column_name] = cleaned[column_name].fillna("unknown")

    missing_after_fill = cleaned.isna().sum()
    handled_missing = (missing_before_fill - missing_after_fill).clip(lower=0)

    invalid_date_rows = int(cleaned["date"].isna().sum())
    invalid_sales_rows = int((cleaned["sales"].isna() | (cleaned["sales"] <= 0)).sum())
    invalid_quantity_rows = 0

    valid_rows = cleaned["date"].notna() & cleaned["sales"].notna() & (cleaned["sales"] > 0)
    if "quantity" in cleaned.columns:
        invalid_quantity_rows = int((cleaned["quantity"].isna() | (cleaned["quantity"] <= 0)).sum())
        valid_rows &= cleaned["quantity"].notna() & (cleaned["quantity"] > 0)

    rows_before_filter = len(cleaned)
    cleaned = cleaned.loc[valid_rows].reset_index(drop=True)
    invalid_rows_removed = rows_before_filter - len(cleaned)

    outlier_rows_removed = 0
    if not cleaned.empty:
        q1 = cleaned["sales"].quantile(0.25)
        q3 = cleaned["sales"].quantile(0.75)
        iqr = q3 - q1

        if pd.notna(iqr) and iqr > 0:
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outlier_mask = (cleaned["sales"] < lower_bound) | (cleaned["sales"] > upper_bound)
            outlier_rows_removed = int(outlier_mask.sum())
            cleaned = cleaned.loc[~outlier_mask].reset_index(drop=True)

    print("\nMissing values handled:")
    handled_missing = handled_missing[handled_missing > 0]
    if handled_missing.empty:
        print("  No missing values needed filling.")
    else:
        for column_name, filled_count in handled_missing.items():
            print(f"  {column_name}: {int(filled_count)} values filled")

    print(f"Duplicates removed: {duplicate_count}")
    print(f"Rows removed for invalid dates: {invalid_date_rows}")
    print(f"Rows removed for invalid sales: {invalid_sales_rows}")
    if "quantity" in cleaned.columns:
        print(f"Rows removed for invalid quantity: {invalid_quantity_rows}")
    print(f"Total invalid rows removed: {invalid_rows_removed}")
    print(f"Outlier rows removed from sales: {outlier_rows_removed}")

    return cleaned, dict(detected_columns)


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Add time, business, customer, and product features."""
    featured = df.copy()
    featured["month"] = featured["date"].dt.month
    featured["year"] = featured["date"].dt.year
    featured["day_of_week"] = featured["date"].dt.day_name().str.lower()
    featured["is_weekend"] = featured["date"].dt.dayofweek >= 5

    if "revenue" not in featured.columns:
        if {"price", "quantity"}.issubset(featured.columns):
            featured["revenue"] = featured["price"] * featured["quantity"]
        else:
            featured["revenue"] = featured["sales"]

    if "customer" in featured.columns:
        featured["total_spend"] = featured.groupby("customer")["sales"].transform("sum")
        featured["order_count"] = featured.groupby("customer")["date"].transform("count")
    else:
        featured["total_spend"] = featured["sales"]
        featured["order_count"] = 1

    if "product" in featured.columns:
        featured["product_total_sales"] = featured.groupby("product")["sales"].transform("sum")
    else:
        featured["product_total_sales"] = featured["sales"]

    return featured


def save_cleaned_data(df: pd.DataFrame, dataset_name: str) -> Path:
    """Save the cleaned dataset in the outputs directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{dataset_name}_cleaned.csv"
    df.to_csv(output_path, index=False)
    return output_path


def main(dataset_choice: str | None = None, load_to_db: bool = True) -> pd.DataFrame:
    """Run the preprocessing pipeline for one selected dataset."""
    dataset_name, raw_df = load_data(dataset_choice)
    cleaned_df, mapping = clean_data(
        df=raw_df,
        column_map=DEFAULT_COLUMN_MAP,
        required_columns=REQUIRED_COLUMNS,
        numeric_columns=NUMERIC_COLUMNS,
    )
    cleaned_df = feature_engineering(cleaned_df)
    cleaned_df["source"] = dataset_name

    required_final_columns = ["date", "customer", "product", "quantity", "price", "sales", "month", "year"]
    default_values = {
        "customer": "unknown",
        "product": "unknown",
        "quantity": pd.NA,
        "price": pd.NA,
        "sales": pd.NA,
        "month": pd.NA,
        "year": pd.NA,
    }

    for column_name in required_final_columns:
        if column_name not in cleaned_df.columns:
            cleaned_df[column_name] = default_values.get(column_name, pd.NA)

    ordered_columns = required_final_columns + [
        column_name for column_name in cleaned_df.columns if column_name not in required_final_columns
    ]
    cleaned_df = cleaned_df[ordered_columns]

    print(f"\nMapping results for {dataset_name}:")
    for standard_name in sorted(mapping):
        print(f"  {standard_name:<10} -> {mapping[standard_name]}")

    print(f"Cleaned shape: {cleaned_df.shape}")

    print("\nData quality report:")
    print("Missing values summary:")
    missing_summary = cleaned_df.isna().sum()
    print(missing_summary[missing_summary > 0].to_string() if (missing_summary > 0).any() else "  No missing values.")

    duplicate_subset = [column_name for column_name in ["date", "product", "customer"] if column_name in cleaned_df.columns]
    duplicate_count = int(cleaned_df.duplicated(subset=duplicate_subset).sum()) if duplicate_subset else 0
    print(f"Duplicate count: {duplicate_count}")

    print("Data types:")
    print(cleaned_df.dtypes.to_string())

    total_revenue = float(cleaned_df["revenue"].sum()) if "revenue" in cleaned_df.columns else float(cleaned_df["sales"].sum())
    total_orders = int(len(cleaned_df))
    average_order_value = total_revenue / total_orders if total_orders else 0.0

    print("\nBusiness metrics:")
    print(f"Total Revenue: {total_revenue:.2f}")
    print(f"Total Orders: {total_orders}")
    print(f"Average Order Value (AOV): {average_order_value:.2f}")

    output_path = save_cleaned_data(cleaned_df, dataset_name)
    print(f"Saved cleaned dataset to: {output_path.resolve()}")

    if load_to_db:
        print("\nStarting Week 3 database load...")
        try:
            load_cleaned_data_to_mysql(cleaned_df)
        except Exception as error:
            print(f"Database load failed: {error}")

    return cleaned_df


if __name__ == "__main__":
    main()
