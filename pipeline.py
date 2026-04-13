from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import pandas as pd


# This script discovers raw retail datasets, standardizes their schemas,
# cleans and enriches them, then writes one cleaned output per source file.
# It is designed to be run locally from the project root.

# ==============================
# Configuration
# ==============================
DEFAULT_COLUMN_MAP: Dict[str, List[str]] = {
    "date": [
        "order_date",
        "order date",
        "date",
        "transaction_date",
        "invoice_date",
        "sales_date",
    ],
    "sales": [
        "total_sales",
        "total sales",
        "sales",
        "revenue",
        "gross_sales",
        "order_value",
    ],
    "product": [
        "product_name",
        "product name",
        "product",
        "item_name",
        "item",
        "sku_name",
    ],
    "customer": [
        "customer_name",
        "customer name",
        "customer",
        "client_name",
        "client",
        "buyer",
    ],
    "quantity": [
        "quantity",
        "qty",
        "order_quantity",
        "units_sold",
        "units",
    ],
    "price": [
        "unit_price",
        "unit price",
        "price",
        "selling_price",
        "unit_cost",
        "rate",
    ],
}

REQUIRED_COLUMNS: Tuple[str, ...] = ("date", "sales")
NUMERIC_COLUMNS: Tuple[str, ...] = ("sales", "price", "quantity")
DISCOVERY_PATTERNS: Tuple[str, ...] = ("*.csv", "*.xlsx", "*.xls")


@dataclass(frozen=True)
class PipelineConfig:
    column_map: Mapping[str, Sequence[str]] = field(default_factory=lambda: DEFAULT_COLUMN_MAP)
    required_columns: Tuple[str, ...] = REQUIRED_COLUMNS
    numeric_columns: Tuple[str, ...] = NUMERIC_COLUMNS
    preview_rows: int = 5
    output_dir: Path = Path("outputs") / "cleaned"


# ==============================
# Normalization Helpers
# ==============================
def normalize_column_name(column_name: str) -> str:
    """
    Convert a raw column label to lowercase snake_case.

    Parameters:
        column_name (str): Original column label from the source dataset.

    Returns:
        str: Normalized column name that is easier to compare consistently.
    """
    normalized = str(column_name).strip()
    normalized = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", normalized)
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"[^0-9a-zA-Z]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized.lower()


def normalize_column_map(column_map: Mapping[str, Sequence[str]]) -> Dict[str, List[str]]:
    """
    Normalize the configured column synonyms so matching works across schemas.

    Parameters:
        column_map (Mapping[str, Sequence[str]]): Canonical column names mapped to
            lists of possible source-column aliases.

    Returns:
        Dict[str, List[str]]: A normalized lookup table keyed by canonical names.
    """
    normalized_map: Dict[str, List[str]] = {}
    for standard_name, aliases in column_map.items():
        candidates = [normalize_column_name(standard_name)]
        candidates.extend(normalize_column_name(alias) for alias in aliases)
        normalized_map[normalize_column_name(standard_name)] = list(dict.fromkeys(candidates))
    return normalized_map


def looks_like_zip(file_path: Path) -> bool:
    """
    Detect whether a file starts with the ZIP signature.

    Parameters:
        file_path (Path): Path to the candidate file.

    Returns:
        bool: True when the file appears to be a ZIP archive, even if it uses a
        misleading extension such as .csv.
    """
    with file_path.open("rb") as file_handle:
        signature = file_handle.read(4)
    return signature.startswith(b"PK\x03\x04")


# ==============================
# Data Loading
# ==============================
def build_csv_read_options(file_path: Path) -> List[Dict[str, object]]:
    """
    Build a list of CSV reader configurations for messy real-world exports.

    Parameters:
        file_path (Path): Source file being inspected for compression hints.

    Returns:
        List[Dict[str, object]]: Candidate pandas.read_csv keyword arguments tried
        in order until one succeeds.
    """
    base_options: Dict[str, object] = {}
    if looks_like_zip(file_path):
        base_options["compression"] = "zip"

    read_options: List[Dict[str, object]] = []
    encodings: Sequence[str | None] = (None, "utf-8-sig", "latin1", "cp1252")

    # Try the common encodings first so we can read messy exports without manual cleanup.
    for encoding in encodings:
        option = dict(base_options)
        if encoding is not None:
            option["encoding"] = encoding
        read_options.append(option)

    # Fall back to the Python engine with delimiter sniffing for loosely formatted CSV files.
    for encoding in encodings:
        option = dict(base_options)
        option["sep"] = None
        option["engine"] = "python"
        if encoding is not None:
            option["encoding"] = encoding
        read_options.append(option)

    return read_options


def load_data(file_path: Path, preview_rows: int = 5) -> pd.DataFrame:
    """
    Load a dataset and print a short inspection summary.

    Parameters:
        file_path (Path): Input dataset to load.
        preview_rows (int): Number of rows to show in the preview output.

    Returns:
        pd.DataFrame: Raw dataset loaded from CSV or Excel.

    Raises:
        ValueError: If no supported read strategy can load the file.
    """
    dataset = None
    read_description = ""
    read_errors: List[str] = []

    if file_path.suffix.lower() in {".xlsx", ".xls"}:
        dataset = pd.read_excel(file_path)
        read_description = "excel"
    else:
        for read_options in build_csv_read_options(file_path):
            try:
                dataset = pd.read_csv(file_path, **read_options)
                option_summary = ", ".join(f"{key}={value}" for key, value in read_options.items())
                read_description = option_summary or "standard csv"
                break
            except Exception as exc:  # noqa: BLE001 - collect all reader failures for debugging.
                read_errors.append(f"{type(exc).__name__}: {exc}")

    if dataset is None:
        error_message = "\n".join(read_errors) if read_errors else "No read strategy succeeded."
        raise ValueError(f"Unable to load dataset: {file_path}\n{error_message}")

    print(f"\n{'=' * 80}")
    print(f"Loaded dataset: {file_path.name}")
    print(f"Read strategy: {read_description}")
    print("-" * 80)
    print("First 5 rows:")
    print(dataset.head(preview_rows).to_string())
    print("-" * 80)
    print(f"Shape: {dataset.shape}")
    print(f"Columns: {list(dataset.columns)}")
    print("Missing values summary:")
    print(dataset.isna().sum().sort_values(ascending=False).to_string())

    return dataset


def detect_columns(df: pd.DataFrame, column_map: Mapping[str, Sequence[str]]) -> Dict[str, str]:
    """
    Match source columns to the pipeline's canonical names.

    Parameters:
        df (pd.DataFrame): Normalized input dataframe.
        column_map (Mapping[str, Sequence[str]]): Canonical names and alias lists.

    Returns:
        Dict[str, str]: Mapping from canonical names to the matched source columns.
    """
    normalized_map = normalize_column_map(column_map)
    detected_columns: Dict[str, str] = {}
    used_columns = set()

    for standard_name, candidates in normalized_map.items():
        for candidate in candidates:
            if candidate in df.columns and candidate not in used_columns:
                detected_columns[standard_name] = candidate
                used_columns.add(candidate)
                break

    return detected_columns


def coalesce_standard_columns(df: pd.DataFrame, detected_columns: Mapping[str, str]) -> pd.DataFrame:
    """
    Rename or merge the detected columns into the canonical schema.

    Parameters:
        df (pd.DataFrame): Input dataframe with normalized column names.
        detected_columns (Mapping[str, str]): Canonical-to-source column mapping.

    Returns:
        pd.DataFrame: Dataframe with standardized column names and merged values.
    """
    standardized = df.copy()

    for standard_name, detected_name in detected_columns.items():
        if detected_name == standard_name:
            continue

        if standard_name in standardized.columns:
            standardized[standard_name] = standardized[standard_name].combine_first(standardized[detected_name])
            standardized = standardized.drop(columns=[detected_name])
        else:
            standardized = standardized.rename(columns={detected_name: standard_name})

    standardized = standardized.loc[:, ~standardized.columns.duplicated()]
    return standardized


def parse_date_series(series: pd.Series) -> pd.Series:
    """
    Parse a date-like series using the strategy that keeps the most valid values.

    Parameters:
        series (pd.Series): Raw date values from the dataset.

    Returns:
        pd.Series: Datetime series with invalid values coerced to NaT.
    """
    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.to_datetime(series, errors="coerce")

    date_options = []
    for day_first in (True, False):
        parsed = pd.to_datetime(series, errors="coerce", dayfirst=day_first)
        date_options.append((parsed.notna().sum(), parsed))

    return max(date_options, key=lambda option: option[0])[1]


def to_numeric_series(series: pd.Series) -> pd.Series:
    """
    Convert loosely formatted numeric text into real numeric values.

    Parameters:
        series (pd.Series): Column containing numbers stored as text.

    Returns:
        pd.Series: Numeric series with invalid entries coerced to NaN.
    """
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    cleaned = cleaned.str.replace(r"[^0-9.\-]", "", regex=True)
    cleaned = cleaned.replace({"": pd.NA, "-": pd.NA, ".": pd.NA, "-.": pd.NA})
    return pd.to_numeric(cleaned, errors="coerce")


def fill_missing_numeric_values(df: pd.DataFrame, numeric_columns: Iterable[str]) -> pd.DataFrame:
    """
    Fill missing numeric values with the median of each column.

    Parameters:
        df (pd.DataFrame): Dataframe containing numeric columns.
        numeric_columns (Iterable[str]): Columns eligible for median imputation.

    Returns:
        pd.DataFrame: Copy of the dataframe with missing numeric values filled.
    """
    completed = df.copy()
    for column_name in numeric_columns:
        if column_name not in completed.columns:
            continue
        median_value = completed[column_name].median(skipna=True)
        if pd.notna(median_value):
            completed[column_name] = completed[column_name].fillna(median_value)
    return completed


# ==============================
# Data Cleaning
# ==============================
def clean_data(
    df: pd.DataFrame,
    column_map: Mapping[str, Sequence[str]],
    required_columns: Sequence[str],
    numeric_columns: Sequence[str],
) -> tuple[pd.DataFrame, Dict[str, str]]:
    """
    Standardize the schema, repair data types, and remove low-quality records.

    Parameters:
        df (pd.DataFrame): Raw input dataframe.
        column_map (Mapping[str, Sequence[str]]): Canonical column names and aliases.
        required_columns (Sequence[str]): Fields that must exist after mapping.
        numeric_columns (Sequence[str]): Columns that should be converted to numeric.

    Returns:
        tuple[pd.DataFrame, Dict[str, str]]: The cleaned dataframe and the detected
        column mapping used during standardization.

    Raises:
        ValueError: If required fields are missing or critical columns cannot be parsed.
    """
    cleaned = df.copy()
    # Normalize all incoming column names first so the rest of the pipeline can
    # work against one predictable naming convention.
    cleaned.columns = [normalize_column_name(column_name) for column_name in cleaned.columns]
    cleaned = cleaned.loc[:, ~cleaned.columns.duplicated()]

    for column_name in cleaned.select_dtypes(include=["object", "string"]).columns:
        cleaned[column_name] = cleaned[column_name].astype("string").str.strip()
        cleaned[column_name] = cleaned[column_name].replace({"": pd.NA})

    detected_columns = detect_columns(cleaned, column_map)
    cleaned = coalesce_standard_columns(cleaned, detected_columns)
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)

    missing_required = [
        column_name
        for column_name in required_columns
        if column_name not in cleaned.columns
        and not (column_name == "sales" and {"price", "quantity"}.issubset(cleaned.columns))
    ]
    if missing_required:
        raise ValueError(
            "Missing required business columns after mapping: "
            + ", ".join(missing_required)
        )

    # Normalize dates early so downstream validation and feature engineering use a single type.
    cleaned["date"] = parse_date_series(cleaned["date"])

    for column_name in numeric_columns:
        if column_name in cleaned.columns:
            cleaned[column_name] = to_numeric_series(cleaned[column_name])

    if "sales" not in cleaned.columns and {"price", "quantity"}.issubset(cleaned.columns):
        # Some datasets only provide unit price and quantity, so derive sales when needed.
        cleaned["sales"] = cleaned["price"] * cleaned["quantity"]
        detected_columns = dict(detected_columns)
        detected_columns["sales"] = "derived_from_price_quantity"

    if cleaned["date"].notna().sum() == 0:
        raise ValueError("Date column could not be parsed into valid datetimes.")
    if cleaned["sales"].notna().sum() == 0:
        raise ValueError("Sales column could not be parsed into valid numeric values.")

    cleaned = fill_missing_numeric_values(cleaned, numeric_columns)
    cleaned = cleaned.dropna(subset=["date", "sales"]).reset_index(drop=True)

    for column_name in ("product", "customer"):
        if column_name in cleaned.columns:
            cleaned[column_name] = cleaned[column_name].fillna("unknown")

    return cleaned, dict(detected_columns)


# ==============================
# Feature Engineering
# ==============================
def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple derived fields that are useful for analysis and forecasting.

    Parameters:
        df (pd.DataFrame): Cleaned dataframe with a parsed date column.

    Returns:
        pd.DataFrame: Dataframe with month, year, and revenue features added.
    """
    featured = df.copy()
    # Extract month and year so downstream charts and aggregations can group by time.
    featured["month"] = featured["date"].dt.month
    featured["year"] = featured["date"].dt.year

    if "revenue" not in featured.columns:
        if "sales" in featured.columns:
            # Reuse sales when revenue is not explicitly provided by the source file.
            featured["revenue"] = featured["sales"]
        elif {"price", "quantity"}.issubset(featured.columns):
            # If sales is missing, derive the same business value from price x quantity.
            featured["revenue"] = featured["price"] * featured["quantity"]

    featured = featured.sort_values("date").reset_index(drop=True)
    return featured


# ==============================
# Reporting and Output
# ==============================
def print_cleaned_summary(dataset_name: str, df: pd.DataFrame, detected_columns: Mapping[str, str]) -> None:
    """
    Print a compact summary of the cleaned dataset.

    Parameters:
        dataset_name (str): Original input filename used for display.
        df (pd.DataFrame): Cleaned and feature-engineered dataframe.
        detected_columns (Mapping[str, str]): Mapping of canonical names to matched columns.

    Returns:
        None
    """
    print(f"\nMapping results for {dataset_name}:")
    for standard_name in sorted(detected_columns):
        print(f"  {standard_name:<10} -> {detected_columns[standard_name]}")

    print("-" * 80)
    print(f"Cleaned shape: {df.shape}")
    print(f"Cleaned columns: {list(df.columns)}")
    print("Cleaned missing values summary:")
    print(df.isna().sum().sort_values(ascending=False).to_string())


def save_cleaned_dataset(df: pd.DataFrame, output_dir: Path, source_path: Path) -> Path:
    """
    Save a cleaned dataset to the output folder using a predictable filename.

    Parameters:
        df (pd.DataFrame): Cleaned dataframe to write.
        output_dir (Path): Destination directory for cleaned files.
        source_path (Path): Original source file used to build the output name.

    Returns:
        Path: Full path to the saved CSV file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{source_path.stem}_cleaned.csv"
    df.to_csv(output_path, index=False)
    return output_path


def discover_input_files(base_dir: Path) -> List[Path]:
    """
    Discover supported raw datasets under a base directory.

    Parameters:
        base_dir (Path): Folder to scan for supported input files.

    Returns:
        List[Path]: Sorted list of raw dataset files found under the folder.
    """
    discovered_files: List[Path] = []
    for pattern in DISCOVERY_PATTERNS:
        discovered_files.extend(base_dir.glob(pattern))

    # Ignore generated outputs and temporary files so reruns only process raw inputs.
    unique_files = {
        file_path.resolve()
        for file_path in discovered_files
        if file_path.is_file()
        and "outputs" not in file_path.parts
        and not file_path.name.startswith("~$")
        and not file_path.stem.endswith("_cleaned")
    }

    return sorted(unique_files)


def run_pipeline(file_paths: Sequence[Path], config: PipelineConfig) -> Dict[str, pd.DataFrame]:
    """
    Process each input file and save a separate cleaned dataset for each one.

    Parameters:
        file_paths (Sequence[Path]): Dataset files to process.
        config (PipelineConfig): Shared pipeline settings.

    Returns:
        Dict[str, pd.DataFrame]: Mapping of input filenames to their processed dataframes.
    """
    processed_datasets: Dict[str, pd.DataFrame] = {}

    for file_path in file_paths:
        # Each dataset goes through the same cleaning and enrichment steps so the
        # outputs stay comparable across source systems.
        raw_data = load_data(file_path=file_path, preview_rows=config.preview_rows)
        cleaned_data, detected_columns = clean_data(
            df=raw_data,
            column_map=config.column_map,
            required_columns=config.required_columns,
            numeric_columns=config.numeric_columns,
        )
        featured_data = feature_engineering(cleaned_data)
        featured_data["source_dataset"] = file_path.stem

        print_cleaned_summary(file_path.name, featured_data, detected_columns)
        saved_path = save_cleaned_dataset(featured_data, config.output_dir, file_path)
        print(f"Saved cleaned dataset to: {saved_path}")

        processed_datasets[file_path.name] = featured_data

    return processed_datasets


# ==============================
# Command-Line Interface
# ==============================
def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for local execution.

    Parameters:
        None

    Returns:
        argparse.Namespace: Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="SalesSense retail analytics preprocessing pipeline."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional list of dataset files. Defaults to auto-discovery in original_dataset.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path("outputs") / "cleaned"),
        help="Directory where cleaned CSV files will be written.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Run the preprocessing pipeline from the command line.

    Parameters:
        None

    Returns:
        None
    """
    args = parse_args()
    # The raw datasets now live under original_dataset, so use that as the default scan root.
    input_root = Path.cwd() / "original_dataset"
    input_files = [Path(file_path).resolve() for file_path in args.files] if args.files else discover_input_files(input_root)

    if not input_files:
        raise ValueError("No supported retail datasets were found in original_dataset.")

    config = PipelineConfig(
        output_dir=Path(args.output_dir),
    )
    run_pipeline(file_paths=input_files, config=config)


if __name__ == "__main__":
    main()
