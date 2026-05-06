from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ml.data_loader import load_cleaned_dataset
from ml.evaluate import build_results_dataframe, evaluate_regression_model, extract_feature_importance, run_week8_evaluation
from ml.models import build_model_specs
from ml.preprocessing import FEATURE_COLUMNS, PreprocessingArtifacts, build_feature_target_frame, prepare_prediction_frame
from ml.train_test_split import split_data


_ACTIVE_DATASET_ID: str | None = None
MODEL_NAME_ALIASES = {
    "lr": "linear_regression",
    "linear": "linear_regression",
    "linear_regression": "linear_regression",
    "rf": "random_forest",
    "random_forest": "random_forest",
    "xgb": "xgboost",
    "xgboost": "xgboost",
}


def _set_active_dataset(dataset_id: str) -> None:
    global _ACTIVE_DATASET_ID
    _ACTIVE_DATASET_ID = dataset_id


def build_output_dir(dataset_id: str) -> Path:
    return Path("outputs") / "ml" / dataset_id


def save_json(output_path: Path, payload: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def save_pickle(output_path: Path, payload: Any) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as file_handle:
        pickle.dump(payload, file_handle)


def load_pickle(input_path: Path) -> Any:
    with input_path.open("rb") as file_handle:
        return pickle.load(file_handle)


def _model_path(output_dir: Path, model_name: str) -> Path:
    return output_dir / f"{model_name}.pkl"


def _save_plot(fig, output_path: Path) -> None:
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _plot_actual_vs_predicted(output_path: Path, y_test: pd.Series, predictions: np.ndarray, display_name: str) -> None:
    fig, axis = plt.subplots(figsize=(7.5, 6))
    axis.scatter(y_test, predictions, alpha=0.7, color="#1f77b4", edgecolors="none")
    min_value = float(min(np.min(y_test), np.min(predictions)))
    max_value = float(max(np.max(y_test), np.max(predictions)))
    axis.plot([min_value, max_value], [min_value, max_value], linestyle="--", color="#d62728", linewidth=1.5)
    axis.set_title(f"Actual vs Predicted - {display_name}")
    axis.set_xlabel("Actual Revenue")
    axis.set_ylabel("Predicted Revenue")
    axis.grid(alpha=0.25)
    _save_plot(fig, output_path)


def _plot_error_distribution(output_path: Path, residuals: np.ndarray, display_name: str) -> None:
    fig, axis = plt.subplots(figsize=(7.5, 6))
    axis.hist(residuals, bins=24, color="#2ca02c", alpha=0.85, edgecolor="white")
    axis.axvline(0, color="#111111", linestyle="--", linewidth=1.2)
    axis.set_title(f"Error Distribution - {display_name}")
    axis.set_xlabel("Prediction Error")
    axis.set_ylabel("Frequency")
    axis.grid(alpha=0.2)
    _save_plot(fig, output_path)


def _plot_model_comparison(output_path: Path, results_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    metric_specs = [("mae", "MAE", "#1f77b4"), ("rmse", "RMSE", "#ff7f0e"), ("r2", "R²", "#2ca02c")]

    for axis, (metric_name, metric_label, color) in zip(axes, metric_specs, strict=False):
        axis.bar(results_df["display_name"], results_df[metric_name], color=color)
        axis.set_title(metric_label)
        axis.tick_params(axis="x", rotation=20)
        axis.grid(axis="y", alpha=0.2)

    fig.suptitle("Model Comparison")
    _save_plot(fig, output_path)


def _plot_fit_comparison(output_path: Path, results_df: pd.DataFrame) -> None:
    fig, axis = plt.subplots(figsize=(8, 4.5))
    x_positions = np.arange(len(results_df))
    width = 0.35
    axis.bar(x_positions - width / 2, results_df["train_r2"], width=width, label="Train R²", color="#9467bd")
    axis.bar(x_positions + width / 2, results_df["test_r2"], width=width, label="Test R²", color="#8c564b")
    axis.set_xticks(x_positions)
    axis.set_xticklabels(results_df["display_name"], rotation=20)
    axis.set_title("Train vs Test R²")
    axis.set_ylabel("R²")
    axis.legend()
    axis.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _load_preprocessing_artifacts(output_dir: Path) -> PreprocessingArtifacts:
    artifacts_path = output_dir / "preprocessing_artifacts.pkl"
    return load_pickle(artifacts_path)


def _resolve_dataset_id_from_input(data: Any) -> str:
    if isinstance(data, pd.DataFrame) and "source" in data.columns:
        unique_sources = data["source"].dropna().astype(str).str.strip().str.lower().unique()
        if len(unique_sources) == 1:
            source_value = unique_sources[0]
            if source_value == "global_ecommerce_sales":
                return "dataset_1"
            if source_value == "retail_supply_chain_sales":
                return "dataset_2"

    if _ACTIVE_DATASET_ID is not None:
        return _ACTIVE_DATASET_ID

    raise ValueError("Dataset context is required for prediction. Run the CLI first or include a source column.")


def _as_dataframe(data: Any) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, dict):
        return pd.DataFrame([data])
    raise TypeError("predict_new expects a pandas DataFrame or a single-row mapping.")


def _load_model(output_dir: Path, model_name: str):
    normalized_name = MODEL_NAME_ALIASES.get(model_name.strip().lower(), model_name.strip().lower())
    model_path = _model_path(output_dir, normalized_name)
    return load_pickle(model_path)


def _build_metrics_payload(dataset_id: str, source_reference: str, features: pd.DataFrame) -> dict[str, Any]:
    return {
        "dataset": dataset_id,
        "source_reference": source_reference,
        "feature_columns": list(features.columns),
        "target_column": "revenue",
        "sample_count": int(len(features)),
        "split": {
            "test_size": 0.2,
            "random_state": 42,
        },
        "models": [],
        "best_model": None,
    }


def run_week7_ml(dataset_choice: str) -> dict[str, Any]:
    dataset_id, cleaned_df, source_reference = load_cleaned_dataset(dataset_choice)
    _set_active_dataset(dataset_id)

    features, target, artifacts = build_feature_target_frame(cleaned_df)
    x_train, x_test, y_train, y_test = split_data(features, target, test_size=0.2, random_state=42)

    output_dir = build_output_dir(dataset_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    save_pickle(output_dir / "preprocessing_artifacts.pkl", artifacts)
    save_pickle(output_dir / "label_encoder.pkl", artifacts.label_encoder)

    model_metrics: dict[str, Any] = _build_metrics_payload(dataset_id, source_reference, features)
    feature_importance_payload: dict[str, Any] = {
        "dataset": dataset_id,
        "source_reference": source_reference,
        "feature_importance": {},
    }

    comparison_rows: list[dict[str, Any]] = []
    overfitting_rows: list[dict[str, Any]] = []

    for spec in build_model_specs():
        model = spec.create()
        model.fit(x_train, y_train)

        metrics = evaluate_regression_model(model, x_train, y_train, x_test, y_test)
        test_predictions = np.asarray(model.predict(x_test))

        save_pickle(_model_path(output_dir, spec.name), model)

        model_record = {
            "name": spec.name,
            "display_name": spec.display_name,
            **metrics,
        }
        model_metrics["models"].append(model_record)
        comparison_rows.append(model_record)
        overfitting_rows.append(
            {
                "display_name": spec.display_name,
                "train_r2": metrics["train_r2"],
                "test_r2": metrics["test_r2"],
                "generalization_gap": metrics["generalization_gap"],
                "fit_assessment": metrics["fit_assessment"],
            }
        )

        _plot_actual_vs_predicted(plots_dir / f"{spec.name}_actual_vs_predicted.png", y_test, test_predictions, spec.display_name)
        _plot_error_distribution(plots_dir / f"{spec.name}_error_distribution.png", np.asarray(y_test) - test_predictions, spec.display_name)

        if spec.name in {"random_forest", "xgboost"}:
            feature_importance_payload["feature_importance"][spec.name] = extract_feature_importance(model, FEATURE_COLUMNS)

        print(f"Model: {spec.display_name}")
        print(f"MAE: {metrics['mae']:.4f}")
        print(f"RMSE: {metrics['rmse']:.4f}")
        print(f"R²: {metrics['r2']:.4f}")
        print(f"Train R²: {metrics['train_r2']:.4f}")
        print(f"Test R²: {metrics['test_r2']:.4f}")
        print(f"Fit: {metrics['fit_assessment']}")
        print()

    results_df = build_results_dataframe(comparison_rows)
    if results_df.empty:
        raise ValueError("No model results were produced.")

    best_row = results_df.iloc[0].to_dict()
    model_metrics["best_model"] = {
        "name": best_row["name"],
        "display_name": best_row["display_name"],
        "r2": float(best_row["r2"]),
    }

    _plot_model_comparison(plots_dir / "model_comparison.png", results_df)
    _plot_fit_comparison(plots_dir / "fit_comparison.png", pd.DataFrame(overfitting_rows))

    save_json(output_dir / "model_metrics.json", model_metrics)
    save_json(output_dir / "feature_importance.json", feature_importance_payload)

    print(f"🏆 BEST MODEL: {best_row['display_name']}")

    return {
        "model_metrics_path": str(output_dir / "model_metrics.json"),
        "feature_importance_path": str(output_dir / "feature_importance.json"),
        "best_model": best_row["display_name"],
        "results_df": results_df,
    }


def predict_new(data, model_name: str):
    """Predict revenue for new rows using one of the saved Week 7 models."""
    dataset_id = _resolve_dataset_id_from_input(data)
    output_dir = build_output_dir(dataset_id)
    artifacts = _load_preprocessing_artifacts(output_dir)
    model = _load_model(output_dir, model_name)
    input_frame = _as_dataframe(data)
    feature_frame = prepare_prediction_frame(input_frame, artifacts)
    return model.predict(feature_frame)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SalesSense ML pipeline.")
    parser.add_argument("--dataset", default="dataset_1", help="dataset_1 or dataset_2")
    parser.add_argument("--mode", default="train", choices=["train", "evaluate"], help="train or evaluate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if args.mode == "evaluate":
            result = run_week8_evaluation(args.dataset)
        else:
            result = run_week7_ml(args.dataset)
    except Exception as exc:
        print(f"Failed to run SalesSense ML pipeline: {exc}")
        return 1

    print("Saved ML outputs:")
    if args.mode == "evaluate":
        print(result["metrics_detailed_path"])
        print(result["final_report_path"])
    else:
        print(result["model_metrics_path"])
        print(result["feature_importance_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
