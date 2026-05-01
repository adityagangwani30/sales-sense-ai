from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def determine_fit_quality(train_score: float, test_score: float) -> str:
    """Classify the model as underfitting, overfitting, or a good fit."""
    if train_score < 0.45 and test_score < 0.45:
        return "Underfitting"
    if train_score - test_score > 0.12 and train_score >= 0.6:
        return "Overfitting"
    return "Good fit"


def evaluate_regression_model(model, x_train, y_train, x_test, y_test) -> dict[str, Any]:
    """Compute the Week 7 regression metrics for one fitted estimator."""
    train_predictions = model.predict(x_train)
    test_predictions = model.predict(x_test)

    train_score = float(r2_score(y_train, train_predictions))
    test_score = float(r2_score(y_test, test_predictions))

    return {
        "mae": float(mean_absolute_error(y_test, test_predictions)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, test_predictions))),
        "r2": test_score,
        "train_r2": train_score,
        "test_r2": test_score,
        "generalization_gap": float(train_score - test_score),
        "fit_assessment": determine_fit_quality(train_score, test_score),
    }


def extract_feature_importance(model, feature_names: list[str]) -> list[dict[str, float]]:
    """Return feature importance scores in the same order as the training features."""
    estimator = model
    if hasattr(model, "named_steps") and "model" in model.named_steps:
        estimator = model.named_steps["model"]

    if not hasattr(estimator, "feature_importances_"):
        return []

    raw_importances = np.asarray(estimator.feature_importances_, dtype=float)
    paired_importances = sorted(
        zip(feature_names, raw_importances, strict=False),
        key=lambda item: item[1],
        reverse=True,
    )
    return [{"feature": feature_name, "importance": round(float(importance), 6)} for feature_name, importance in paired_importances]


def build_results_dataframe(results: list[dict[str, Any]]) -> pd.DataFrame:
    """Create a sortable comparison table for the trained models."""
    frame = pd.DataFrame(results)
    if frame.empty:
        return frame
    return frame.sort_values(["r2", "rmse"], ascending=[False, True]).reset_index(drop=True)
