from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.evaluation import evaluate_models
from src.feature_engineering import apply_feature_engineering
from src.insights import export_project_outputs, summarize_artifacts
from src.model_training import ensure_trained_models
from src.preprocessing import run_preprocessing_stage, summarize_dataframe


def _configure_logging(dataset_choice: str) -> Path:
    dataset_root = Path("outputs") / dataset_choice
    reports_dir = dataset_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    log_path = reports_dir / "pipeline.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )
    return log_path


def run_week9_pipeline(dataset_choice: str) -> dict[str, Any]:
    start_time = time.perf_counter()
    logging.info("Step started: load_data")
    cleaned_df = run_preprocessing_stage(dataset_choice)
    logging.info("Step completed: load_data")

    logging.info("Step started: preprocess")
    cleaned_summary = summarize_dataframe(cleaned_df)
    logging.info("Step completed: preprocess")

    logging.info("Step started: feature_engineering")
    featured_df = apply_feature_engineering(cleaned_df)
    logging.info("Step completed: feature_engineering")

    logging.info("Step started: train_models")
    training_result = ensure_trained_models(dataset_choice)
    logging.info("Step completed: train_models")

    logging.info("Step started: evaluate_models")
    evaluation_result = evaluate_models(dataset_choice)
    logging.info("Step completed: evaluate_models")

    logging.info("Step started: generate_insights")
    export_result = export_project_outputs(dataset_choice)
    logging.info("Step completed: generate_insights")

    total_seconds = time.perf_counter() - start_time
    logging.info("Step completed: export_outputs")
    logging.info("Execution time: %.2f seconds", total_seconds)

    return {
        "dataset": dataset_choice,
        "cleaned_summary": cleaned_summary,
        "featured_rows": int(len(featured_df)),
        "training": training_result,
        "evaluation": evaluation_result,
        "export": export_result,
        "structured_summary": summarize_artifacts(dataset_choice),
        "execution_seconds": total_seconds,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SalesSense AI Week 9 production pipeline.")
    parser.add_argument("--dataset", default="dataset_1", help="dataset_1 or dataset_2")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    log_path = _configure_logging(args.dataset)

    try:
        result = run_week9_pipeline(args.dataset)
    except Exception as exc:
        logging.exception("Pipeline failed for %s", args.dataset)
        print(f"Failed to run Week 9 pipeline: {exc}")
        return 1

    print("Saved project outputs:")
    print(result["export"]["metrics_dir"])
    print(result["export"]["reports_dir"])
    print(result["export"]["plots_dir"])
    print(f"Log file: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
