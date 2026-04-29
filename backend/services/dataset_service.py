from __future__ import annotations

from typing import Any

from pipeline import run_pipeline


ALLOWED_DATASETS = {"dataset_1", "dataset_2"}


class InvalidDatasetError(ValueError):
    """Raised when a request tries to access an unsupported dataset."""


def validate_dataset(dataset: str) -> str:
    """Normalize and validate the public dataset identifier."""
    normalized = dataset.strip().lower()
    if normalized not in ALLOWED_DATASETS:
        raise InvalidDatasetError("Invalid dataset")
    return normalized


def load_dataset(dataset: str) -> dict[str, Any]:
    """Run the existing pipeline for one dataset without touching the other one.

    Dataset isolation is critical here because the database stores multiple sources
    in the same schema. Keeping the pipeline scoped to one validated dataset and
    preserving its source value prevents cross-dataset contamination.
    """
    dataset_name = validate_dataset(dataset)
    print(f"Processing dataset: {dataset_name}")

    cleaned_df = run_pipeline(
        dataset_name=dataset_name,
        reset_db=False,
        load_to_db=True,
        run_sql=True,
        run_visuals=True,
        sync_frontend_assets=True,
    )

    return {
        "dataset": dataset_name,
        "rows_processed": int(len(cleaned_df)),
        "message": "Dataset loaded successfully",
    }
