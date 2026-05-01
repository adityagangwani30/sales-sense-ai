from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from typing import Final

import pandas as pd


OUTPUTS_DIR: Final[Path] = Path("outputs")

DATASET_ALIASES: Final[dict[str, str]] = {
    "1": "dataset_1",
    "dataset_1": "dataset_1",
    "global_ecommerce_sales": "dataset_1",
    "global_ecommerce_sales.csv": "dataset_1",
    "2": "dataset_2",
    "dataset_2": "dataset_2",
    "retail_supply_chain_sales": "dataset_2",
    "retail_supply_chain_sales.csv": "dataset_2",
    "retail-supply-chain-sales-dataset": "dataset_2",
    "retail-supply-chain-sales-dataset.xlsx": "dataset_2",
}

SOURCE_DATASET_IDS: Final[dict[str, str]] = {
    "dataset_1": "global_ecommerce_sales",
    "dataset_2": "retail_supply_chain_sales",
}

MYSQL_FEATURE_QUERY: Final[str] = """
    SELECT
        f.source,
        f.revenue,
        f.month,
        f.year,
        f.customer_id,
        f.product_id,
        o.order_date AS date,
        o.quantity,
        p.price,
        p.category
    FROM fact_sales AS f
    LEFT JOIN orders AS o
        ON o.order_id = f.order_id
       AND o.source = f.source
    LEFT JOIN products AS p
        ON p.product_id = f.product_id
       AND p.source = f.source
    WHERE f.source = %s
"""


def resolve_dataset_id(dataset_choice: str) -> str:
    """Map a user choice to one canonical dataset identifier."""
    normalized_choice = dataset_choice.strip().lower()
    return DATASET_ALIASES.get(normalized_choice, normalized_choice)


def get_cleaned_dataset_path(dataset_id: str) -> Path:
    """Return the dataset-specific cleaned CSV path."""
    source_dataset_id = SOURCE_DATASET_IDS[dataset_id]
    return OUTPUTS_DIR / source_dataset_id / f"{source_dataset_id}_cleaned.csv"


def _load_dataset_from_mysql(dataset_id: str) -> pd.DataFrame | None:
    """Load one dataset from MySQL when the relational tables are available."""
    with suppress(ImportError):
        from database_loader import connect_db

        try:
            connection = connect_db()
        except Exception:
            return None

        try:
            source_name = SOURCE_DATASET_IDS[dataset_id]
            cursor = connection.cursor()
            try:
                cursor.execute(MYSQL_FEATURE_QUERY, (source_name,))
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                frame = pd.DataFrame(rows, columns=columns)
            finally:
                cursor.close()
        except Exception:
            return None
        finally:
            connection.close()

        return frame if not frame.empty else None


def _validate_source_isolated(frame: pd.DataFrame, dataset_id: str, source_reference: str) -> None:
    if "source" not in frame.columns:
        return

    unique_sources = frame["source"].dropna().astype(str).str.strip().str.lower().unique()
    if len(unique_sources) > 1:
        raise ValueError(f"Mixed dataset sources found in {source_reference}: {unique_sources.tolist()}")

    expected_source_id = SOURCE_DATASET_IDS[dataset_id]
    if len(unique_sources) == 1 and unique_sources[0] != expected_source_id:
        raise ValueError(
            f"Dataset source mismatch in {source_reference}: expected {expected_source_id}, found {unique_sources[0]}"
        )


def load_cleaned_dataset(dataset_choice: str) -> tuple[str, pd.DataFrame, str]:
    """Load one dataset from MySQL first, then fall back to the cleaned CSV output."""
    dataset_id = resolve_dataset_id(dataset_choice)

    if dataset_id not in {"dataset_1", "dataset_2"}:
        valid_choices = ", ".join(["dataset_1", "dataset_2"])
        raise ValueError(f"Invalid dataset choice: {dataset_choice}. Choose one of: {valid_choices}")

    mysql_frame = _load_dataset_from_mysql(dataset_id)
    if mysql_frame is not None:
        source_reference = f"MySQL fact_sales WHERE source = {SOURCE_DATASET_IDS[dataset_id]}"
        _validate_source_isolated(mysql_frame, dataset_id, source_reference)
        return dataset_id, mysql_frame, source_reference

    cleaned_path = get_cleaned_dataset_path(dataset_id)

    if not cleaned_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {cleaned_path}")

    frame = pd.read_csv(cleaned_path, low_memory=False)
    _validate_source_isolated(frame, dataset_id, str(cleaned_path))

    return dataset_id, frame, str(cleaned_path)
