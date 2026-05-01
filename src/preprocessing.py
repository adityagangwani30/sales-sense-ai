from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from pipeline import run_pipeline as legacy_run_pipeline


def run_preprocessing_stage(
    dataset_choice: str,
    *,
    load_to_db: bool = True,
    reset_db: bool = True,
    run_sql: bool = True,
    run_visuals: bool = True,
    sync_frontend_assets: bool = True,
) -> pd.DataFrame:
    """Run the existing data pipeline stage for one dataset only."""
    logging.info("Preprocessing started for %s", dataset_choice)
    cleaned_df = legacy_run_pipeline(
        dataset_name=dataset_choice,
        load_to_db=load_to_db,
        reset_db=reset_db,
        run_sql=run_sql,
        run_visuals=run_visuals,
        sync_frontend_assets=sync_frontend_assets,
    )
    logging.info("Preprocessing completed for %s", dataset_choice)
    return cleaned_df


def summarize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Return a compact dataset summary for logs and reports."""
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "missing_values": int(df.isna().sum().sum()),
    }
