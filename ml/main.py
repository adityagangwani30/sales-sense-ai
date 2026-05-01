from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.data_loader import load_cleaned_dataset
from ml.evaluate import evaluate_regression_model, extract_feature_importance
from ml.models import build_model_specs
from ml.preprocessing import build_feature_target_frame
from ml.train_test_split import split_data


def build_output_dir(dataset_id: str) -> Path:
    return Path("outputs") / "ml" / dataset_id


def save_json(output_path: Path, payload: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_week6_ml(dataset_choice: str) -> dict[str, Any]:
    dataset_id, cleaned_df, cleaned_path = load_cleaned_dataset(dataset_choice)
    features, target = build_feature_target_frame(cleaned_df)
    x_train, x_test, y_train, y_test = split_data(features, target, test_size=0.2, random_state=42)

    output_dir = build_output_dir(dataset_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_metrics: dict[str, Any] = {
        "dataset": dataset_id,
        "cleaned_dataset_path": str(cleaned_path),
        "feature_columns": list(features.columns),
        "target_column": "sales",
        "sample_count": int(len(features)),
        "models": {},
    }
    feature_importance_payload: dict[str, Any] = {
        "dataset": dataset_id,
        "cleaned_dataset_path": str(cleaned_path),
        "feature_importance": {},
    }

    for spec in build_model_specs():
        model = spec.pipeline
        model.fit(x_train, y_train)

        metrics = evaluate_regression_model(model, x_train, y_train, x_test, y_test)
        model_metrics["models"][spec.name] = {
            "display_name": spec.display_name,
            **metrics,
        }

        if spec.name in {"decision_tree", "random_forest"}:
            feature_importance_payload["feature_importance"][spec.name] = extract_feature_importance(model)

        print(f"Model: {spec.display_name}")
        print(f"MAE: {metrics['mae']:.4f}")
        print(f"R2: {metrics['r2']:.4f}")
        print(f"Train R2: {metrics['train_r2']:.4f}")
        print(f"Test R2: {metrics['test_r2']:.4f}")
        print(f"Fit: {metrics['fit_assessment']}")
        print()

    save_json(output_dir / "model_metrics.json", model_metrics)
    save_json(output_dir / "feature_importance.json", feature_importance_payload)

    return {
        "model_metrics_path": str(output_dir / "model_metrics.json"),
        "feature_importance_path": str(output_dir / "feature_importance.json"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SalesSense Week 6 ML baseline.")
    parser.add_argument("--dataset", default="dataset_1", help="dataset_1 or dataset_2")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        result = run_week6_ml(args.dataset)
    except Exception as exc:
        print(f"Failed to run Week 6 ML pipeline: {exc}")
        return 1

    print("Saved ML outputs:")
    print(result["model_metrics_path"])
    print(result["feature_importance_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
