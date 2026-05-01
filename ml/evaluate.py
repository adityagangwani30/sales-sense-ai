from __future__ import annotations

import json
import pickle
import calendar
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, cross_val_score

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ml.data_loader import load_cleaned_dataset
from ml.models import build_model_specs
from ml.preprocessing import FEATURE_COLUMNS, PreprocessingArtifacts, build_feature_target_frame
from ml.train_test_split import split_data


def determine_fit_quality(train_score: float, test_score: float) -> str:
    """Classify the model as underfitting, overfitting, or a good fit."""
    if train_score < 0.45 and test_score < 0.45:
        return "Underfitting"
    if train_score - test_score > 0.12 and train_score >= 0.6:
        return "Overfitting"
    return "Good fit"


def _adjusted_r2(r2_value: float, sample_count: int, feature_count: int) -> float:
    if sample_count <= feature_count + 1:
        return float(r2_value)
    return float(1 - (1 - r2_value) * (sample_count - 1) / (sample_count - feature_count - 1))


def _mean_absolute_percentage_error(y_true: pd.Series | np.ndarray, y_pred: np.ndarray) -> float:
    actual = np.asarray(y_true, dtype=float)
    predicted = np.asarray(y_pred, dtype=float)
    non_zero_mask = actual != 0
    if not np.any(non_zero_mask):
        return 0.0
    percentage_errors = np.abs((actual[non_zero_mask] - predicted[non_zero_mask]) / actual[non_zero_mask])
    return float(np.mean(percentage_errors) * 100)


def _safe_pct_error(actual: pd.Series | np.ndarray, predicted: np.ndarray) -> np.ndarray:
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        pct_error = np.where(actual_array != 0, np.abs((actual_array - predicted_array) / actual_array) * 100, np.nan)
    return pct_error


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (pd.Series, pd.Index)):
        return value.tolist()
    return str(value)


def evaluate_regression_model(model, x_train, y_train, x_test, y_test) -> dict[str, Any]:
    """Compute the Week 7 regression metrics for one fitted estimator."""
    train_predictions = model.predict(x_train)
    test_predictions = model.predict(x_test)

    train_score = float(r2_score(y_train, train_predictions))
    test_score = float(r2_score(y_test, test_predictions))
    mse = float(mean_squared_error(y_test, test_predictions))
    mae = float(mean_absolute_error(y_test, test_predictions))
    rmse = float(np.sqrt(mse))
    mape = float(_mean_absolute_percentage_error(y_test, test_predictions))
    adjusted_r2 = _adjusted_r2(test_score, len(y_test), x_test.shape[1])

    return {
        "mae": mae,
        "mse": mse,
        "rmse": rmse,
        "r2": test_score,
        "adjusted_r2": adjusted_r2,
        "mape": mape,
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


def _save_json(output_path: Path, payload: Any) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, default=_json_default), encoding="utf-8")


def _save_pickle(output_path: Path, payload: Any) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as file_handle:
        pickle.dump(payload, file_handle)


def _load_pickle(input_path: Path) -> Any:
    with input_path.open("rb") as file_handle:
        return pickle.load(file_handle)


def _model_path(output_dir: Path, model_name: str) -> Path:
    return output_dir / f"{model_name}.pkl"


def _load_preprocessing_artifacts(output_dir: Path) -> PreprocessingArtifacts:
    return _load_pickle(output_dir / "preprocessing_artifacts.pkl")


def _resolve_estimator(model: Any) -> Any:
    if hasattr(model, "named_steps") and "model" in getattr(model, "named_steps", {}):
        return model.named_steps["model"]
    return model


def _normalize_importances(raw_importances: np.ndarray) -> np.ndarray:
    importances = np.asarray(raw_importances, dtype=float)
    total = float(importances.sum())
    if total <= 0:
        return np.zeros_like(importances, dtype=float)
    return importances / total * 100.0


def _model_based_importance(model: Any, feature_names: list[str]) -> pd.DataFrame:
    estimator = _resolve_estimator(model)
    raw_importances: np.ndarray | None = None

    if hasattr(estimator, "feature_importances_"):
        raw_importances = np.asarray(estimator.feature_importances_, dtype=float)
    elif hasattr(estimator, "coef_"):
        raw_importances = np.abs(np.asarray(estimator.coef_, dtype=float)).ravel()

    if raw_importances is None:
        raw_importances = np.zeros(len(feature_names), dtype=float)

    if raw_importances.size != len(feature_names):
        raw_importances = np.resize(raw_importances, len(feature_names))

    percentages = _normalize_importances(raw_importances)
    frame = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": percentages,
            "raw_importance": raw_importances,
        }
    )
    return frame.sort_values("importance", ascending=False).reset_index(drop=True)


def _permutation_importance_frame(model: Any, x_test: pd.DataFrame, y_test: pd.Series, feature_names: list[str]) -> pd.DataFrame:
    importance_result = permutation_importance(
        model,
        x_test,
        y_test,
        n_repeats=15,
        random_state=42,
        scoring="r2",
        n_jobs=-1,
    )
    raw_importances = np.maximum(np.asarray(importance_result.importances_mean, dtype=float), 0.0)
    percentages = _normalize_importances(raw_importances)
    frame = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": percentages,
            "raw_importance": raw_importances,
        }
    )
    return frame.sort_values("importance", ascending=False).reset_index(drop=True)


def _plot_error_histogram(output_path: Path, residuals: np.ndarray, display_name: str) -> None:
    fig, axis = plt.subplots(figsize=(7.5, 5.5))
    axis.hist(residuals, bins=24, color="#2563eb", alpha=0.85, edgecolor="white")
    axis.axvline(0, color="#111111", linestyle="--", linewidth=1.2)
    axis.set_title(f"Error Histogram - {display_name}")
    axis.set_xlabel("Residual")
    axis.set_ylabel("Frequency")
    axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _plot_residual_plot(output_path: Path, predictions: np.ndarray, residuals: np.ndarray, display_name: str) -> None:
    fig, axis = plt.subplots(figsize=(7.5, 5.5))
    axis.scatter(predictions, residuals, alpha=0.7, color="#16a34a", edgecolors="none")
    axis.axhline(0, color="#111111", linestyle="--", linewidth=1.2)
    axis.set_title(f"Residual Plot - {display_name}")
    axis.set_xlabel("Predicted Revenue")
    axis.set_ylabel("Residual")
    axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _plot_error_box(output_path: Path, residuals: np.ndarray, display_name: str) -> None:
    fig, axis = plt.subplots(figsize=(6.5, 5.5))
    axis.boxplot(residuals, vert=True, patch_artist=True, boxprops={"facecolor": "#f59e0b"})
    axis.set_title(f"Box Plot - {display_name}")
    axis.set_ylabel("Residual")
    axis.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _plot_error_qq(output_path: Path, residuals: np.ndarray, display_name: str) -> None:
    fig, axis = plt.subplots(figsize=(6.5, 5.5))
    stats.probplot(residuals, dist="norm", plot=axis)
    axis.set_title(f"Q-Q Plot - {display_name}")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _save_error_analysis(output_dir: Path, y_test: pd.Series, predictions: np.ndarray, display_name: str) -> tuple[dict[str, Any], pd.DataFrame]:
    residuals = np.asarray(y_test, dtype=float) - np.asarray(predictions, dtype=float)
    analysis = {
        "dataset": output_dir.name,
        "model": display_name,
        "mean_error": float(np.mean(residuals)),
        "median_error": float(np.median(residuals)),
        "std_error": float(np.std(residuals, ddof=1)) if residuals.size > 1 else 0.0,
        "min_error": float(np.min(residuals)),
        "max_error": float(np.max(residuals)),
        "percentiles": {
            "5": float(np.percentile(residuals, 5)),
            "25": float(np.percentile(residuals, 25)),
            "50": float(np.percentile(residuals, 50)),
            "75": float(np.percentile(residuals, 75)),
            "95": float(np.percentile(residuals, 95)),
        },
    }

    error_dir = output_dir / "plots" / "error_analysis"
    error_dir.mkdir(parents=True, exist_ok=True)
    _plot_error_histogram(error_dir / "error_histogram.png", residuals, display_name)
    _plot_residual_plot(error_dir / "residual_plot.png", np.asarray(predictions, dtype=float), residuals, display_name)
    _plot_error_box(error_dir / "box_plot.png", residuals, display_name)
    _plot_error_qq(error_dir / "qq_plot.png", residuals, display_name)

    return analysis, pd.DataFrame({"error": residuals})


def _build_worst_predictions_frame(x_test: pd.DataFrame, y_test: pd.Series, predictions: np.ndarray) -> pd.DataFrame:
    actual = np.asarray(y_test, dtype=float)
    predicted = np.asarray(predictions, dtype=float)
    errors = actual - predicted
    pct_error = _safe_pct_error(actual, predicted)
    frame = x_test.copy().reset_index(drop=True)
    frame.insert(0, "Actual", actual)
    frame.insert(1, "Predicted", predicted)
    frame.insert(2, "Error", errors)
    frame.insert(3, "Abs_Error", np.abs(errors))
    frame.insert(4, "Pct_Error", pct_error)
    return frame.sort_values("Abs_Error", ascending=False).reset_index(drop=True)


def _build_percentage_error_analysis(worst_predictions: pd.DataFrame) -> dict[str, Any]:
    pct_error = worst_predictions["Pct_Error"].replace([np.inf, -np.inf], np.nan).dropna()
    if pct_error.empty:
        return {
            "mean_mape": 0.0,
            "median_mape": 0.0,
            "within_5_percent": 0.0,
            "within_10_percent": 0.0,
            "within_20_percent": 0.0,
        }

    return {
        "mean_mape": float(pct_error.mean()),
        "median_mape": float(pct_error.median()),
        "within_5_percent": float((pct_error <= 5).mean() * 100),
        "within_10_percent": float((pct_error <= 10).mean() * 100),
        "within_20_percent": float((pct_error <= 20).mean() * 100),
    }


def _cross_validate_model(model: Any, x_train: pd.DataFrame, y_train: pd.Series) -> dict[str, Any]:
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_r2_scores = cross_val_score(clone(model), x_train, y_train, cv=cv, scoring="r2", n_jobs=-1)
    cv_scores = cross_validate(
        clone(model),
        x_train,
        y_train,
        cv=cv,
        scoring={
            "r2": "r2",
            "mae": "neg_mean_absolute_error",
            "rmse": "neg_root_mean_squared_error",
        },
        return_train_score=False,
        n_jobs=-1,
    )

    return {
        "folds": 5,
        "r2_scores": [float(score) for score in cv_r2_scores],
        "mae_scores": [float(abs(score)) for score in cv_scores["test_mae"]],
        "rmse_scores": [float(abs(score)) for score in cv_scores["test_rmse"]],
        "mean_r2": float(np.mean(cv_r2_scores)),
        "std_r2": float(np.std(cv_r2_scores, ddof=1)) if len(cv_r2_scores) > 1 else 0.0,
        "mean_mae": float(np.mean(np.abs(cv_scores["test_mae"]))),
        "mean_rmse": float(np.mean(np.abs(cv_scores["test_rmse"]))),
    }


def _assess_overfitting(train_r2: float, test_r2: float, cv_r2: float) -> str:
    train_gap = train_r2 - test_r2
    cv_gap = train_r2 - cv_r2
    if train_gap <= 0.04 and cv_gap <= 0.04:
        return "Good fit"
    if train_gap <= 0.12 and cv_gap <= 0.12:
        return "Slight overfitting"
    return "Overfitting"


def _summarize_model_model_based_importance(model: Any, feature_names: list[str]) -> pd.DataFrame:
    return _model_based_importance(model, feature_names)


def _build_feature_importance_payload(
    model: Any,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    feature_names: list[str],
) -> dict[str, Any]:
    model_based = _summarize_model_model_based_importance(model, feature_names)
    permutation = _permutation_importance_frame(model, x_test, y_test, feature_names)
    comparison = model_based.merge(permutation, on="feature", how="inner", suffixes=("_model", "_permutation"))

    selected_features = model_based.loc[model_based["importance"] >= 1.0, "feature"].tolist()
    if not selected_features:
        selected_features = model_based.head(min(3, len(model_based)))["feature"].tolist()

    return {
        "model_based_importance": model_based.to_dict(orient="records"),
        "permutation_importance": permutation.to_dict(orient="records"),
        "comparison": comparison.to_dict(orient="records"),
        "selected_low_importance_threshold": 1.0,
        "selected_features": selected_features,
    }


def _build_feature_selection_results(
    model: Any,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    selected_features: list[str],
    original_metrics: dict[str, Any],
) -> dict[str, Any]:
    reduced_model = clone(model)
    reduced_model.fit(x_train[selected_features], y_train)
    reduced_metrics = evaluate_regression_model(
        reduced_model,
        x_train[selected_features],
        y_train,
        x_test[selected_features],
        y_test,
    )

    return {
        "selected_features": selected_features,
        "original_metrics": {
            "r2": original_metrics["r2"],
            "mae": original_metrics["mae"],
            "rmse": original_metrics["rmse"],
        },
        "reduced_metrics": {
            "r2": reduced_metrics["r2"],
            "mae": reduced_metrics["mae"],
            "rmse": reduced_metrics["rmse"],
        },
        "delta": {
            "r2": float(reduced_metrics["r2"] - original_metrics["r2"]),
            "mae": float(reduced_metrics["mae"] - original_metrics["mae"]),
            "rmse": float(reduced_metrics["rmse"] - original_metrics["rmse"]),
        },
    }


def _generate_business_insights(df: pd.DataFrame) -> str:
    revenue_series = pd.to_numeric(df["revenue"], errors="coerce")
    numeric_candidates = [
        column_name
        for column_name in df.columns
        if column_name not in {"revenue", "date", "customer", "product", "order_id", "ship_date", "source"}
        and pd.api.types.is_numeric_dtype(pd.to_numeric(df[column_name], errors="coerce"))
    ]

    correlation_rows: list[tuple[str, float]] = []
    for column_name in numeric_candidates:
        series = pd.to_numeric(df[column_name], errors="coerce")
        if series.notna().sum() < 2:
            continue
        correlation = series.corr(revenue_series)
        if pd.notna(correlation):
            correlation_rows.append((column_name, float(correlation)))

    correlation_rows.sort(key=lambda item: abs(item[1]), reverse=True)
    top_drivers = correlation_rows[:5]

    month_totals = df.groupby("month", dropna=True)["revenue"].sum().sort_values(ascending=False)
    best_month = int(month_totals.index[0]) if not month_totals.empty else None
    worst_month = int(month_totals.index[-1]) if not month_totals.empty else None

    product_column = "product" if "product" in df.columns else "product_id"
    product_totals = df.groupby(product_column, dropna=True)["revenue"].sum().sort_values(ascending=False)
    top_products = product_totals.head(5)
    bottom_products = product_totals.tail(5)

    if "is_weekend" in df.columns:
        weekend_totals = df.groupby("is_weekend")["revenue"].agg(["mean", "sum", "count"])
    else:
        weekend_totals = pd.DataFrame()

    lines = [
        f"Dataset: {df['source'].iloc[0] if 'source' in df.columns else 'unknown'}",
        "",
        "Revenue Drivers",
    ]
    if top_drivers:
        for rank, (column_name, correlation) in enumerate(top_drivers, start=1):
            lines.append(f"{rank}. {column_name}: correlation {correlation:.3f}")
    else:
        lines.append("No stable numeric drivers were detected.")

    lines.extend([
        "",
        "Seasonal Insights",
    ])
    if best_month is not None and worst_month is not None:
        lines.append(f"Best month: {calendar.month_name[best_month]}.")
        lines.append(f"Worst month: {calendar.month_name[worst_month]}.")
    else:
        lines.append("Month-level seasonal signals were not available.")

    lines.extend([
        "",
        "Product Insights",
        "Top products:",
    ])
    if not top_products.empty:
        for product_name, revenue_value in top_products.items():
            lines.append(f"- {product_name}: {float(revenue_value):.2f}")
    else:
        lines.append("- No product ranking available.")

    lines.append("Bottom products:")
    if not bottom_products.empty:
        for product_name, revenue_value in bottom_products.items():
            lines.append(f"- {product_name}: {float(revenue_value):.2f}")
    else:
        lines.append("- No product ranking available.")

    lines.extend([
        "",
        "Customer Insights",
    ])
    if not weekend_totals.empty:
        weekday_mean = float(weekend_totals.loc[False, "mean"]) if False in weekend_totals.index else float("nan")
        weekend_mean = float(weekend_totals.loc[True, "mean"]) if True in weekend_totals.index else float("nan")
        lines.append(f"Weekend average revenue: {weekend_mean:.2f}")
        lines.append(f"Weekday average revenue: {weekday_mean:.2f}")
    else:
        lines.append("Weekend vs weekday trend could not be derived.")

    return "\n".join(lines)


def _build_confidence_scores(model: Any, x_test: pd.DataFrame) -> dict[str, Any]:
    estimator = _resolve_estimator(model)
    if not hasattr(estimator, "estimators_"):
        return {
            "confidence_levels": [],
            "summary": "Random Forest confidence scoring is unavailable for this model.",
        }

    x_test_values = x_test.to_numpy()
    tree_predictions = np.asarray([tree.predict(x_test_values) for tree in estimator.estimators_], dtype=float)
    mean_prediction = tree_predictions.mean(axis=0)
    lower_bound = np.percentile(tree_predictions, 10, axis=0)
    upper_bound = np.percentile(tree_predictions, 90, axis=0)
    interval_width = upper_bound - lower_bound
    relative_width = interval_width / np.maximum(np.abs(mean_prediction), 1.0)

    confidence_level = np.where(relative_width <= 0.10, "High confidence", np.where(relative_width <= 0.20, "Medium confidence", "Low confidence"))
    confidence_frame = pd.DataFrame(
        {
            "prediction": mean_prediction,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "interval_width": interval_width,
            "relative_width": relative_width,
            "confidence_level": confidence_level,
        }
    )

    return {
        "summary": {
            "mean_interval_width": float(np.mean(interval_width)),
            "median_interval_width": float(np.median(interval_width)),
            "high_confidence_count": int((confidence_frame["confidence_level"] == "High confidence").sum()),
            "medium_confidence_count": int((confidence_frame["confidence_level"] == "Medium confidence").sum()),
            "low_confidence_count": int((confidence_frame["confidence_level"] == "Low confidence").sum()),
        },
        "thresholds": {
            "high": 0.10,
            "medium": 0.20,
        },
        "samples": confidence_frame.head(25).to_dict(orient="records"),
    }


def _build_roi_analysis(worst_predictions: pd.DataFrame, sample_count: int) -> str:
    residuals = worst_predictions["Error"]
    actuals = worst_predictions["Actual"]
    understock = float(np.maximum(actuals - worst_predictions["Predicted"], 0).sum())
    overstock = float(np.maximum(worst_predictions["Predicted"] - actuals, 0).sum())

    understock_savings = understock * 0.15
    overstock_savings = overstock * 0.10
    annual_savings = (understock_savings + overstock_savings) * max(sample_count / max(len(worst_predictions), 1), 1.0)
    implementation_cost = max(annual_savings * 0.20, 1.0)
    roi_percent = ((annual_savings - implementation_cost) / implementation_cost) * 100 if implementation_cost else 0.0

    return "\n".join(
        [
            "ROI Analysis",
            f"Overstock reduction opportunity: {overstock_savings:.2f}",
            f"Understock reduction opportunity: {understock_savings:.2f}",
            f"Annual savings: {annual_savings:.2f}",
            f"Estimated implementation cost: {implementation_cost:.2f}",
            f"ROI %: {roi_percent:.2f}%",
            f"Average absolute test error: {float(np.mean(np.abs(residuals))):.2f}",
        ]
    )


def _build_final_report(
    dataset_id: str,
    best_model_name: str,
    best_metrics: dict[str, Any],
    error_analysis: dict[str, Any],
    feature_importance_payload: dict[str, Any],
    business_insights: str,
    roi_text: str,
) -> str:
    top_model_features = feature_importance_payload["model_based_importance"][:5]
    feature_lines = [f"- {item['feature']}: {item['importance']:.2f}%" for item in top_model_features]

    return "\n".join(
        [
            f"SalesSense AI - Final Report ({dataset_id})",
            "",
            f"Best model: {best_model_name}",
            f"R²: {best_metrics['r2']:.3f}",
            f"Adjusted R²: {best_metrics['adjusted_r2']:.3f}",
            f"MAE: ${best_metrics['mae']:.2f}",
            f"RMSE: ${best_metrics['rmse']:.2f}",
            f"MAPE: {best_metrics['mape']:.2f}%",
            f"Fit assessment: {best_metrics['fit_assessment']}",
            "",
            "Error Insights",
            f"Mean error: {error_analysis['mean_error']:.2f}",
            f"Median error: {error_analysis['median_error']:.2f}",
            f"Std error: {error_analysis['std_error']:.2f}",
            "",
            "Feature Importance",
            *feature_lines,
            "",
            "Business Recommendations",
            business_insights,
            "",
            roi_text,
        ]
    )


def run_week8_evaluation(dataset_choice: str) -> dict[str, Any]:
    dataset_id, cleaned_df, source_reference = load_cleaned_dataset(dataset_choice)
    features, target, artifacts = build_feature_target_frame(cleaned_df)
    x_train, x_test, y_train, y_test = split_data(features, target, test_size=0.2, random_state=42)

    output_dir = Path("outputs") / "ml" / dataset_id
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "plots").mkdir(parents=True, exist_ok=True)

    _save_pickle(output_dir / "preprocessing_artifacts.pkl", artifacts)
    _save_pickle(output_dir / "label_encoder.pkl", artifacts.label_encoder)

    model_records: list[dict[str, Any]] = []
    loaded_models: dict[str, Any] = {}
    for spec in build_model_specs():
        model_file = _model_path(output_dir, spec.name)
        if not model_file.exists():
            raise FileNotFoundError(f"Missing trained model artifact: {model_file}")
        loaded_models[spec.name] = _load_pickle(model_file)

        model = loaded_models[spec.name]
        metrics = evaluate_regression_model(model, x_train, y_train, x_test, y_test)
        model_records.append(
            {
                "name": spec.name,
                "display_name": spec.display_name,
                **metrics,
            }
        )

    results_df = build_results_dataframe(model_records)
    if results_df.empty:
        raise ValueError("No trained models were available for evaluation.")

    best_row = results_df.iloc[0].to_dict()
    best_model_name = str(best_row["name"])
    best_model = loaded_models[best_model_name]

    best_predictions = np.asarray(best_model.predict(x_test), dtype=float)
    residuals = np.asarray(y_test, dtype=float) - best_predictions
    error_analysis, _ = _save_error_analysis(output_dir, y_test, best_predictions, str(best_row["display_name"]))
    worst_predictions = _build_worst_predictions_frame(x_test, y_test, best_predictions)
    percentage_error = _build_percentage_error_analysis(worst_predictions)
    cross_validation = _cross_validate_model(best_model, x_train, y_train)
    overfitting_state = _assess_overfitting(float(best_row["train_r2"]), float(best_row["test_r2"]), cross_validation["mean_r2"])

    feature_importance_payload = _build_feature_importance_payload(best_model, x_test, y_test, list(features.columns))
    feature_selection_results = _build_feature_selection_results(
        best_model,
        x_train,
        y_train,
        x_test,
        y_test,
        feature_importance_payload["selected_features"],
        best_row,
    )

    business_insights = _generate_business_insights(cleaned_df)
    confidence_scores = _build_confidence_scores(loaded_models.get("random_forest", best_model), x_test)
    roi_text = _build_roi_analysis(worst_predictions, len(cleaned_df))

    metrics_payload = {
        "dataset": dataset_id,
        "source_reference": source_reference,
        "feature_columns": list(features.columns),
        "target_column": "revenue",
        "sample_count": int(len(features)),
        "split": {
            "test_size": 0.2,
            "random_state": 42,
        },
        "models": model_records,
        "best_model": {
            "name": best_row["name"],
            "display_name": best_row["display_name"],
            "r2": float(best_row["r2"]),
            "mae": float(best_row["mae"]),
            "rmse": float(best_row["rmse"]),
            "mape": float(best_row["mape"]),
        },
    }

    _save_json(output_dir / "metrics_detailed.json", metrics_payload)
    _save_json(output_dir / "model_metrics.json", metrics_payload)
    _save_json(output_dir / "error_analysis.json", error_analysis)
    _save_json(output_dir / "percentage_error.json", percentage_error)
    _save_json(output_dir / "cross_validation.json", cross_validation)
    _save_json(output_dir / "feature_importance.json", feature_importance_payload)
    _save_json(output_dir / "feature_selection_results.json", feature_selection_results)
    _save_json(output_dir / "confidence_scores.json", confidence_scores)
    _save_json(output_dir / "roi_analysis.json", {"text": roi_text})

    worst_predictions_output = worst_predictions.head(10).copy()
    worst_predictions_output.to_csv(output_dir / "worst_predictions.csv", index=False)

    (output_dir / "business_insights.txt").write_text(business_insights, encoding="utf-8")
    (output_dir / "roi_analysis.txt").write_text(roi_text, encoding="utf-8")

    final_report = _build_final_report(
        dataset_id,
        str(best_row["display_name"]),
        best_row,
        error_analysis,
        feature_importance_payload,
        business_insights,
        roi_text,
    )
    (output_dir / "final_report.txt").write_text(final_report, encoding="utf-8")

    print(f"Model: {best_row['display_name']}")
    print(f"MAE: ${best_row['mae']:.2f}")
    print(f"RMSE: ${best_row['rmse']:.2f}")
    print(f"R²: {best_row['r2']:.4f}")
    print(f"MAPE: {best_row['mape']:.2f}%")
    print(f"Mean R²: {cross_validation['mean_r2']:.3f}")
    print(f"Std Dev: {cross_validation['std_r2']:.3f}")
    print(f"Fit: {best_row['fit_assessment']}")
    print(f"Overfitting check: {overfitting_state}")

    return {
        "dataset": dataset_id,
        "output_dir": str(output_dir),
        "best_model": best_row["display_name"],
        "metrics_detailed_path": str(output_dir / "metrics_detailed.json"),
        "error_analysis_path": str(output_dir / "error_analysis.json"),
        "cross_validation_path": str(output_dir / "cross_validation.json"),
        "feature_importance_path": str(output_dir / "feature_importance.json"),
        "feature_selection_results_path": str(output_dir / "feature_selection_results.json"),
        "business_insights_path": str(output_dir / "business_insights.txt"),
        "confidence_scores_path": str(output_dir / "confidence_scores.json"),
        "roi_analysis_path": str(output_dir / "roi_analysis.txt"),
        "final_report_path": str(output_dir / "final_report.txt"),
    }
