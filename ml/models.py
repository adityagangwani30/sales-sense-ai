from __future__ import annotations

from dataclasses import dataclass

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

from ml.preprocessing import build_preprocessor


@dataclass(frozen=True)
class ModelSpec:
    """Container for one trainable model definition."""

    name: str
    display_name: str
    pipeline: Pipeline


def build_model_specs() -> list[ModelSpec]:
    """Create the Week 6 baseline regressors."""
    return [
        ModelSpec(
            name="linear_regression",
            display_name="Linear Regression",
            pipeline=Pipeline(
                [
                    ("preprocessor", build_preprocessor(scale_numeric=True)),
                    ("model", LinearRegression()),
                ]
            ),
        ),
        ModelSpec(
            name="decision_tree",
            display_name="Decision Tree",
            pipeline=Pipeline(
                [
                    ("preprocessor", build_preprocessor(scale_numeric=False)),
                    (
                        "model",
                        DecisionTreeRegressor(random_state=42),
                    ),
                ]
            ),
        ),
        ModelSpec(
            name="random_forest",
            display_name="Random Forest",
            pipeline=Pipeline(
                [
                    ("preprocessor", build_preprocessor(scale_numeric=False)),
                    (
                        "model",
                        RandomForestRegressor(
                            n_estimators=100,
                            random_state=42,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
        ),
    ]
