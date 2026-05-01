from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

from ml.data_loader import resolve_dataset_id


_METRIC_FILE_NAMES = {
    "metrics_detailed.json",
    "model_metrics.json",
    "error_analysis.json",
    "percentage_error.json",
    "cross_validation.json",
    "feature_importance.json",
    "feature_selection_results.json",
    "confidence_scores.json",
    "roi_analysis.json",
}

_REPORT_FILE_NAMES = {
    "final_report.txt",
    "business_insights.txt",
    "roi_analysis.txt",
    "worst_predictions.csv",
}


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _copy_tree(source_dir: Path, destination_dir: Path) -> None:
    if not source_dir.exists():
        return

    for path in source_dir.rglob("*"):
        if path.is_dir():
            continue
        relative_path = path.relative_to(source_dir)
        destination_path = destination_dir / relative_path
        _copy_file(path, destination_path)


def export_project_outputs(dataset_choice: str) -> dict[str, str]:
    """Mirror the Week 8 ML artifacts into the cleaner Week 9 structure."""
    dataset_id = resolve_dataset_id(dataset_choice)
    source_dir = Path("outputs") / "ml" / dataset_id
    structured_root = Path("outputs") / dataset_id
    metrics_dir = structured_root / "metrics"
    plots_dir = structured_root / "plots"
    reports_dir = structured_root / "reports"
    models_dir = Path("models") / dataset_id

    logging.info("Exporting structured outputs for %s", dataset_id)
    structured_root.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    if source_dir.exists():
        for file_path in source_dir.glob("*.json"):
            destination = metrics_dir / file_path.name if file_path.name in _METRIC_FILE_NAMES else reports_dir / file_path.name
            _copy_file(file_path, destination)

        for file_path in source_dir.glob("*.txt"):
            destination = reports_dir / file_path.name if file_path.name in _REPORT_FILE_NAMES else metrics_dir / file_path.name
            _copy_file(file_path, destination)

        for file_path in source_dir.glob("*.csv"):
            destination = reports_dir / file_path.name
            _copy_file(file_path, destination)

        _copy_tree(source_dir / "plots", plots_dir)

        for file_path in source_dir.glob("*.pkl"):
            _copy_file(file_path, models_dir / file_path.name)

    return {
        "dataset": dataset_id,
        "metrics_dir": str(metrics_dir),
        "plots_dir": str(plots_dir),
        "reports_dir": str(reports_dir),
        "models_dir": str(models_dir),
    }


def summarize_artifacts(dataset_choice: str) -> dict[str, Any]:
    """Create a compact summary for logs and the README."""
    dataset_id = resolve_dataset_id(dataset_choice)
    structured_root = Path("outputs") / dataset_id
    return {
        "dataset": dataset_id,
        "structured_root": str(structured_root),
        "metrics_files": sorted([path.name for path in (structured_root / "metrics").glob("*")]) if structured_root.exists() else [],
        "report_files": sorted([path.name for path in (structured_root / "reports").glob("*")]) if structured_root.exists() else [],
    }
