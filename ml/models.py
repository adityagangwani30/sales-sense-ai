from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor


@dataclass(frozen=True)
class ModelSpec:
    """Container for one trainable model definition."""

    name: str
    display_name: str
    factory: Callable[[], object]

    def create(self) -> object:
        return self.factory()


def build_model_specs() -> list[ModelSpec]:
    """Create the Week 7 baseline regressors."""
    return [
        ModelSpec(
            name="linear_regression",
            display_name="Linear Regression",
            factory=lambda: LinearRegression(),
        ),
        ModelSpec(
            name="random_forest",
            display_name="Random Forest",
            factory=lambda: RandomForestRegressor(
                n_estimators=300,
                max_depth=12,
                min_samples_split=4,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            ),
        ),
        ModelSpec(
            name="xgboost",
            display_name="XGBoost",
            factory=lambda: XGBRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.9,
                colsample_bytree=0.85,
                reg_alpha=0.0,
                reg_lambda=1.0,
                min_child_weight=1,
                objective="reg:squarederror",
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
