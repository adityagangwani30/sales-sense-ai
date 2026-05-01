from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score


def determine_fit_quality(train_score: float, test_score: float) -> str:
    """Classify the model as underfitting, overfitting, or a good fit."""
    if train_score < 0.5 and test_score < 0.5:
        return "Underfitting"
    if train_score - test_score > 0.15 and train_score >= 0.6:
        return "Overfitting"
    return "Good fit"


def evaluate_regression_model(model, x_train, y_train, x_test, y_test) -> dict[str, Any]:
    """Compute the Week 6 regression metrics for one fitted pipeline."""
    train_predictions = model.predict(x_train)
    test_predictions = model.predict(x_test)

    train_score = float(r2_score(y_train, train_predictions))
    test_score = float(r2_score(y_test, test_predictions))

    return {
        "mae": float(mean_absolute_error(y_test, test_predictions)),
        "r2": test_score,
        "train_r2": train_score,
        "test_r2": test_score,
        "generalization_gap": float(train_score - test_score),
        "fit_assessment": determine_fit_quality(train_score, test_score),
    }


def _collapse_feature_name(transformed_name: str) -> str:
    base_name = transformed_name.split("__", 1)[-1]
    return base_name.split("_", 1)[0]


def extract_feature_importance(model) -> list[dict[str, float]]:
    """Aggregate transformed feature importances back to the project features."""
    preprocessor = model.named_steps["preprocessor"]
    estimator = model.named_steps["model"]

    if not hasattr(estimator, "feature_importances_"):
        return []

    transformed_names = preprocessor.get_feature_names_out()
    raw_importances = np.asarray(estimator.feature_importances_, dtype=float)

    grouped_importances: dict[str, float] = defaultdict(float)
    for transformed_name, importance in zip(transformed_names, raw_importances, strict=False):
        grouped_importances[_collapse_feature_name(str(transformed_name))] += float(importance)

    sorted_importances = sorted(grouped_importances.items(), key=lambda item: item[1], reverse=True)
    return [{"feature": feature_name, "importance": round(importance, 6)} for feature_name, importance in sorted_importances]
