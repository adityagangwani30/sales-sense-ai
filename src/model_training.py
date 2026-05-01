from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ml.data_loader import resolve_dataset_id
from ml.main import run_week7_ml
from ml.models import build_model_specs


def _model_output_dir(dataset_choice: str) -> Path:
    dataset_id = resolve_dataset_id(dataset_choice)
    return Path("outputs") / "ml" / dataset_id


def _expected_model_paths(dataset_choice: str) -> list[Path]:
    output_dir = _model_output_dir(dataset_choice)
    return [output_dir / f"{spec.name}.pkl" for spec in build_model_specs()]


def ensure_trained_models(dataset_choice: str) -> dict[str, Any]:
    """Reuse saved Week 7 models and train only if an artifact is missing."""
    output_dir = _model_output_dir(dataset_choice)
    expected_paths = _expected_model_paths(dataset_choice)
    missing_paths = [path for path in expected_paths if not path.exists()]

    if missing_paths:
        logging.info("Training models for %s because artifacts are missing.", dataset_choice)
        result = run_week7_ml(dataset_choice)
        return {
            "dataset": resolve_dataset_id(dataset_choice),
            "status": "trained",
            "output_dir": str(output_dir),
            "artifacts": result,
        }

    logging.info("Training skipped for %s; saved model artifacts already exist.", dataset_choice)
    return {
        "dataset": resolve_dataset_id(dataset_choice),
        "status": "skipped",
        "output_dir": str(output_dir),
        "artifacts": {},
    }
