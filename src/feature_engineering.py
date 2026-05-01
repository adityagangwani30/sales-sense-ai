from __future__ import annotations

import logging

import pandas as pd

from pipeline import feature_engineering as legacy_feature_engineering


def apply_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the shared feature engineering logic used by the existing pipeline."""
    logging.info("Feature engineering started")
    featured_df = legacy_feature_engineering(df)
    logging.info("Feature engineering completed")
    return featured_df
