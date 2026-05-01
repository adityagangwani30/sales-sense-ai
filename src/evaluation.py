from __future__ import annotations

import logging
from typing import Any

from ml.main import run_week8_evaluation


def evaluate_models(dataset_choice: str) -> dict[str, Any]:
    """Run the Week 8 evaluation pipeline on one dataset only."""
    logging.info("Evaluation started for %s", dataset_choice)
    result = run_week8_evaluation(dataset_choice)
    logging.info("Evaluation completed for %s", dataset_choice)
    return result
