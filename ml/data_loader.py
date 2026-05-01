from __future__ import annotations

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


def resolve_dataset_id(dataset_choice: str) -> str:
    """Map a user choice to one canonical dataset identifier."""
    normalized_choice = dataset_choice.strip().lower()
    return DATASET_ALIASES.get(normalized_choice, normalized_choice)


def get_cleaned_dataset_path(dataset_id: str) -> Path:
    """Return the dataset-specific cleaned CSV path."""
    source_dataset_id = SOURCE_DATASET_IDS[dataset_id]
    return OUTPUTS_DIR / source_dataset_id / f"{source_dataset_id}_cleaned.csv"


def load_cleaned_dataset(dataset_choice: str) -> tuple[str, pd.DataFrame, Path]:
    """Load exactly one cleaned dataset from the pipeline outputs."""
    dataset_id = resolve_dataset_id(dataset_choice)
    cleaned_path = get_cleaned_dataset_path(dataset_id)

    if dataset_id not in {"dataset_1", "dataset_2"}:
        valid_choices = ", ".join(["dataset_1", "dataset_2"])
        raise ValueError(f"Invalid dataset choice: {dataset_choice}. Choose one of: {valid_choices}")

    if not cleaned_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {cleaned_path}")

    frame = pd.read_csv(cleaned_path, low_memory=False)

    if "source" in frame.columns:
        unique_sources = frame["source"].dropna().astype(str).str.strip().str.lower().unique()
        if len(unique_sources) > 1:
            raise ValueError(f"Mixed dataset sources found in {cleaned_path}: {unique_sources.tolist()}")
        expected_source_id = SOURCE_DATASET_IDS[dataset_id]
        if len(unique_sources) == 1 and unique_sources[0] != expected_source_id:
            raise ValueError(
                f"Dataset source mismatch in {cleaned_path}: expected {expected_source_id}, found {unique_sources[0]}"
            )

    return dataset_id, frame, cleaned_path
