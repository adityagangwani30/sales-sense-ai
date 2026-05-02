from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd


OUTPUTS_DIR = Path("outputs")
FRONTEND_PUBLIC_DIR = Path("frontend") / "public"
FRONTEND_DATA_DIR = FRONTEND_PUBLIC_DIR / "data"
FRONTEND_DATASETS_DIR = FRONTEND_DATA_DIR / "datasets"
FRONTEND_SQL_DIR = FRONTEND_DATA_DIR / "sql-analysis"
FRONTEND_VISUALIZATION_DIR = FRONTEND_PUBLIC_DIR / "visualizations"

DATASET_CONFIGS = [
    {
        "id": "dataset_1",
        "label": "Global E-Commerce Sales",
        "description": "E-Commerce sales analytics with global customer and product data",
        "source_path": OUTPUTS_DIR / "dataset_1" / "dataset_1_cleaned.csv",
        "ml_id": "dataset_1",
        "aliases": ["global_ecommerce_sales"],
    },
    {
        "id": "dataset_2",
        "label": "Retail Supply Chain Sales",
        "description": "Retail supply chain performance and sales metrics",
        "source_path": OUTPUTS_DIR / "dataset_2" / "dataset_2_cleaned.csv",
        "ml_id": "dataset_2",
        "aliases": ["retail_supply_chain_sales"],
    },
]

ML_ARTIFACTS_TO_COPY = [
    "model_metrics.json",
    "feature_importance.json",
    "error_analysis.json",
    "confidence_scores.json",
    "roi_analysis.json",
    "percentage_error.json",
    "business_insights.txt",
    "cross_validation.json",
    "metrics_detailed.json",
]

ROOT_ML_ARTIFACTS = {
    "business_insights.txt",
    "model_metrics.json",
}

VISUALIZATION_TITLES = {
    "monthly_revenue_trend.png": "Monthly Revenue Trend",
    "top_products.png": "Top Products Performance",
    "category_distribution.png": "Category Revenue Distribution",
    "customer_segmentation.png": "Customer Segmentation Overview",
    "order_value_distribution.png": "Order Value Distribution",
    "price_vs_sales_scatter.png": "Price vs Sales Correlation",
    "sales_dashboard.png": "Executive Analytics Dashboard",
}


def ensure_frontend_dirs() -> None:
    """Create the frontend public directories used by the dashboard."""
    for directory in (
        FRONTEND_DATA_DIR,
        FRONTEND_DATASETS_DIR,
        FRONTEND_SQL_DIR,
        FRONTEND_VISUALIZATION_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create ML subdirectories for each dataset
    for config in DATASET_CONFIGS:
        ml_dir = FRONTEND_DATA_DIR / config["id"] / "ml"
        ml_dir.mkdir(parents=True, exist_ok=True)


def get_dataset_output_dir(dataset_id: str) -> Path:
    return OUTPUTS_DIR / dataset_id


def get_sql_output_dir(dataset_id: str) -> Path:
    return get_dataset_output_dir(dataset_id) / "sql_analysis"


def get_visualization_output_dir(dataset_id: str) -> Path:
    return get_dataset_output_dir(dataset_id) / "visualizations"


def get_ml_output_dir(ml_dataset_id: str) -> Path:
    """Get the ML output directory for a dataset."""
    return OUTPUTS_DIR / "ml" / ml_dataset_id


def detect_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first matching column name from a preference list."""
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def format_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a DataFrame into JSON-serializable records."""
    cleaned = df.copy()
    for column_name in cleaned.columns:
        if pd.api.types.is_datetime64_any_dtype(cleaned[column_name]):
            cleaned[column_name] = cleaned[column_name].dt.strftime("%Y-%m-%d")
    cleaned = cleaned.where(pd.notna(cleaned), None)
    return cleaned.to_dict(orient="records")


def copy_visualizations(dataset_id: str) -> list[dict[str, str]]:
    """Copy generated PNGs into the Next.js public folder."""
    visualization_dir = get_visualization_output_dir(dataset_id)
    if not visualization_dir.exists():
        print(f"  [WARN] Skipping visualizations for {dataset_id}: folder not found")
        return []

    target_dir = FRONTEND_VISUALIZATION_DIR / dataset_id
    target_dir.mkdir(parents=True, exist_ok=True)

    assets: list[dict[str, str]] = []
    for image_path in sorted(visualization_dir.glob("*.png")):
        target_path = target_dir / image_path.name
        shutil.copy2(image_path, target_path)
        assets.append(
            {
                "title": VISUALIZATION_TITLES.get(image_path.name, image_path.stem.replace("_", " ").title()),
                "src": f"/visualizations/{dataset_id}/{image_path.name}",
                "filename": image_path.name,
            }
        )
    return assets


def copy_ml_artifacts(dataset_id: str, ml_dataset_id: str) -> None:
    """Copy ML output artifacts into the frontend public data folder."""
    ml_output_dir = get_ml_output_dir(ml_dataset_id)
    if not ml_output_dir.exists():
        print(f"  [WARN] No ML artifacts found for {dataset_id} (looking in {ml_output_dir})")
        return

    target_dir = FRONTEND_DATA_DIR / "ml" / ml_dataset_id
    target_dir.mkdir(parents=True, exist_ok=True)
    root_dataset_dir = FRONTEND_DATA_DIR / dataset_id
    root_dataset_dir.mkdir(parents=True, exist_ok=True)

    copied_count = 0
    for artifact_name in ML_ARTIFACTS_TO_COPY:
        source_path = ml_output_dir / artifact_name
        if source_path.exists():
            target_path = target_dir / artifact_name
            shutil.copy2(source_path, target_path)
            copied_count += 1

            if artifact_name in ROOT_ML_ARTIFACTS:
                shutil.copy2(source_path, root_dataset_dir / artifact_name)

    if copied_count > 0:
        print(f"  [OK] Copied {copied_count} ML artifacts for {dataset_id}")
    else:
        print(f"  [WARN] No ML artifacts copied for {dataset_id}: files not found")


def export_sql_analysis_json(dataset_id: str) -> dict[str, str]:
    """Publish every SQL analysis CSV as frontend-friendly JSON."""
    sql_output_dir = get_sql_output_dir(dataset_id)
    if not sql_output_dir.exists():
        print(f"  [WARN] No SQL analysis found for {dataset_id}")
        return {}

    target_dir = FRONTEND_SQL_DIR / dataset_id
    target_dir.mkdir(parents=True, exist_ok=True)

    exported_files: dict[str, str] = {}
    for csv_path in sorted(sql_output_dir.glob("*.csv")):
        frame = pd.read_csv(csv_path)

        if csv_path.stem == "category_performance" and "total_revenue" in frame.columns:
            total_rev = frame["total_revenue"].sum()
            if total_rev and total_rev > 0:
                frame["share_pct"] = (frame["total_revenue"] / total_rev) * 100
            else:
                frame["share_pct"] = 0.0

        output_path = target_dir / f"{csv_path.stem}.json"
        output_path.write_text(json.dumps(format_records(frame), indent=2), encoding="utf-8")
        exported_files[csv_path.stem] = f"/data/sql-analysis/{dataset_id}/{csv_path.stem}.json"
    return exported_files


def prepare_category_distribution(df: pd.DataFrame, category_column: str, value_column: str) -> list[dict[str, Any]]:
    """Summarize category performance and keep the pie chart readable."""
    category_df = (
        df.groupby(category_column, dropna=False)[value_column]
        .sum()
        .reset_index(name="total_revenue")
        .sort_values("total_revenue", ascending=False)
    )
    category_df[category_column] = category_df[category_column].fillna("Unknown")

    if len(category_df) > 6:
        head = category_df.head(5).copy()
        other_total = category_df.iloc[5:]["total_revenue"].sum()
        category_df = pd.concat(
            [head, pd.DataFrame([{category_column: "Other", "total_revenue": other_total}])],
            ignore_index=True,
        )

    total_revenue = category_df["total_revenue"].sum()
    category_df["share_pct"] = (
        (category_df["total_revenue"] / total_revenue) * 100 if total_revenue else 0
    )
    category_df = category_df.rename(columns={category_column: "category"})
    return format_records(category_df)


def build_dataset_payload(
    cleaned_path: Path,
    dataset_id: str,
    label: str,
    description: str,
    visualizations: list[dict[str, str]],
) -> dict[str, Any]:
    """Create one dashboard payload from a generated cleaned dataset."""
    if not cleaned_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {cleaned_path}")

    df = pd.read_csv(cleaned_path, parse_dates=["date"], low_memory=False)

    sales_column = detect_column(df, ["sales", "revenue"])
    order_column = detect_column(df, ["order_id"])
    customer_column = detect_column(df, ["customer_id", "customer"])
    product_column = detect_column(df, ["product"])
    category_column = detect_column(df, ["product_category", "category", "sub_category"])
    segment_column = detect_column(df, ["customer_segment", "segment"])
    price_column = detect_column(df, ["price"])

    if sales_column is None or customer_column is None or product_column is None:
        raise ValueError(f"Dataset {dataset_id} is missing one of the required dashboard fields.")

    df[sales_column] = pd.to_numeric(df[sales_column], errors="coerce")
    if price_column:
        df[price_column] = pd.to_numeric(df[price_column], errors="coerce")

    total_revenue = float(df[sales_column].fillna(0).sum())
    total_orders = int(df[order_column].nunique()) if order_column else int(len(df))
    total_customers = int(df[customer_column].nunique())
    average_order_value = total_revenue / total_orders if total_orders else 0.0

    monthly_revenue = (
        df.dropna(subset=["date"])
        .assign(month_start=lambda frame: frame["date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month_start", as_index=False)[sales_column]
        .sum()
        .rename(columns={sales_column: "revenue"})
        .sort_values("month_start")
    )
    monthly_revenue["month"] = monthly_revenue["month_start"].dt.strftime("%b %Y")
    monthly_revenue["month_start"] = monthly_revenue["month_start"].dt.strftime("%Y-%m-%d")
    revenue_trend = format_records(monthly_revenue[["month", "month_start", "revenue"]])

    top_products = (
        df.groupby(product_column, dropna=False)
        .agg(
            total_revenue=(sales_column, "sum"),
            order_count=(order_column, "nunique") if order_column else (sales_column, "size"),
        )
        .reset_index()
        .rename(columns={product_column: "product_name"})
        .sort_values("total_revenue", ascending=False)
        .head(10)
    )
    top_products["product_name"] = top_products["product_name"].fillna("Unknown")

    category_distribution = (
        prepare_category_distribution(df, category_column, sales_column) if category_column else []
    )

    customer_segmentation: list[dict[str, Any]] = []
    if segment_column:
        segment_df = (
            df.groupby(segment_column, dropna=False)
            .agg(
                customer_count=(customer_column, "nunique"),
                avg_order_value=(sales_column, "mean"),
            )
            .reset_index()
            .rename(columns={segment_column: "segment"})
            .sort_values("customer_count", ascending=False)
        )
        segment_df["segment"] = segment_df["segment"].fillna("Unknown")
        customer_segmentation = format_records(segment_df)

    top_customers = (
        df.groupby(customer_column, dropna=False)[sales_column]
        .sum()
        .reset_index(name="total_spent")
        .rename(columns={customer_column: "customer_name"})
        .sort_values("total_spent", ascending=False)
        .head(8)
    )
    top_customers["customer_name"] = top_customers["customer_name"].fillna("Unknown")

    repeat_purchase_rate = 0.0
    if order_column:
        customer_orders = df.groupby(customer_column, dropna=False)[order_column].nunique()
        repeat_purchase_rate = (
            float((customer_orders > 1).sum()) / float(len(customer_orders)) * 100 if len(customer_orders) else 0.0
        )

    trend_change_pct = 0.0
    if len(monthly_revenue) >= 2:
        previous_revenue = float(monthly_revenue["revenue"].iloc[-2])
        latest_revenue = float(monthly_revenue["revenue"].iloc[-1])
        trend_change_pct = ((latest_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue else 0.0

    peak_month = None
    if revenue_trend:
        peak_month = max(revenue_trend, key=lambda item: float(item["revenue"]))["month"]

    payload = {
        "datasetId": dataset_id,
        "label": label,
        "description": description,
        "sourceFile": str(cleaned_path).replace("\\", "/"),
        "kpis": {
            "totalRevenue": round(total_revenue, 2),
            "totalOrders": total_orders,
            "totalCustomers": total_customers,
            "averageOrderValue": round(average_order_value, 2),
            "repeatPurchaseRate": round(repeat_purchase_rate, 2),
            "trendChangePct": round(trend_change_pct, 2),
        },
        "revenueTrend": revenue_trend,
        "topProducts": format_records(top_products),
        "categoryDistribution": category_distribution,
        "customerSegmentation": customer_segmentation,
        "topCustomers": format_records(top_customers),
        "visualizations": visualizations,
        "highlights": {
            "peakMonth": peak_month,
            "topProduct": format_records(top_products.head(1))[0]["product_name"] if not top_products.empty else None,
            "largestCategory": category_distribution[0]["category"] if category_distribution else None,
        },
        "priceSalesCorrelationAvailable": bool(price_column),
    }
    return payload


def export_dataset_jsons() -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    """Build a dataset payload for each source file the dashboard can switch between."""
    dataset_entries: list[dict[str, str]] = []
    sql_analysis_entries: dict[str, dict[str, str]] = {}
    for config in DATASET_CONFIGS:
        if not config["source_path"].exists():
            print(f"  [WARN] Skipping {config['id']}: cleaned dataset not found")
            continue

        if not get_sql_output_dir(config["id"]).exists():
            print(f"  [WARN] Skipping {config['id']}: SQL analysis not found")
            continue

        visualizations = copy_visualizations(config["id"])
        copy_ml_artifacts(config["id"], config["ml_id"])
        sql_analysis_entries[config["id"]] = export_sql_analysis_json(config["id"])
        payload = build_dataset_payload(
            cleaned_path=config["source_path"],
            dataset_id=config["id"],
            label=config["label"],
            description=config["description"],
            visualizations=visualizations,
        )
        output_path = FRONTEND_DATASETS_DIR / f"{config['id']}.json"
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        # Also write individual dataset JSON files under /public/data/<dataset>/
        per_dataset_dir = FRONTEND_DATA_DIR / config["id"]
        per_dataset_dir.mkdir(parents=True, exist_ok=True)

        # metrics.json: include both snake_case and camelCase keys for compatibility
        kpis = payload.get("kpis", {})
        metrics_obj = {
            "total_revenue": kpis.get("totalRevenue"),
            "totalRevenue": kpis.get("totalRevenue"),
            "total_orders": kpis.get("totalOrders"),
            "totalOrders": kpis.get("totalOrders"),
            "total_customers": kpis.get("totalCustomers"),
            "totalCustomers": kpis.get("totalCustomers"),
            "avg_order_value": kpis.get("averageOrderValue"),
            "averageOrderValue": kpis.get("averageOrderValue"),
            "repeat_purchase_rate": kpis.get("repeatPurchaseRate"),
            "repeatPurchaseRate": kpis.get("repeatPurchaseRate"),
            "trend_change_pct": kpis.get("trendChangePct"),
            "trendChangePct": kpis.get("trendChangePct"),
        }
        (per_dataset_dir / "metrics.json").write_text(json.dumps(metrics_obj, indent=2), encoding="utf-8")

        # revenue_trend.json
        (per_dataset_dir / "revenue_trend.json").write_text(json.dumps(payload.get("revenueTrend", []), indent=2), encoding="utf-8")

        # top_products.json
        (per_dataset_dir / "top_products.json").write_text(json.dumps(payload.get("topProducts", []), indent=2), encoding="utf-8")

        # customer_segmentation.json
        (per_dataset_dir / "customer_segmentation.json").write_text(json.dumps(payload.get("customerSegmentation", []), indent=2), encoding="utf-8")

        # category_performance.json
        (per_dataset_dir / "category_performance.json").write_text(json.dumps(payload.get("categoryDistribution", []), indent=2), encoding="utf-8")

        # repeat_rate.json
        repeat_obj = {"repeat_purchase_rate": kpis.get("repeatPurchaseRate")} 
        (per_dataset_dir / "repeat_rate.json").write_text(json.dumps(repeat_obj, indent=2), encoding="utf-8")

        # insights.json (highlights)
        (per_dataset_dir / "insights.json").write_text(json.dumps(payload.get("highlights", {}), indent=2), encoding="utf-8")
        dataset_entries.append(
            {
                "id": config["id"],
                "label": config["label"],
                "description": config["description"],
                "dataPath": f"/data/datasets/{config['id']}.json",
            }
        )
    return dataset_entries, sql_analysis_entries


def copy_to_alias_dirs(dataset_id: str, aliases: list[str]) -> None:
    """Copy dataset files to alias directories for backward compatibility."""
    source_dir = FRONTEND_DATA_DIR / dataset_id
    source_sql_dir = FRONTEND_SQL_DIR / dataset_id
    source_viz_dir = FRONTEND_VISUALIZATION_DIR / dataset_id

    for alias in aliases:
        alias_dir = FRONTEND_DATA_DIR / alias
        alias_sql_dir = FRONTEND_SQL_DIR / alias
        alias_viz_dir = FRONTEND_VISUALIZATION_DIR / alias

        if source_dir.exists():
            alias_dir.mkdir(parents=True, exist_ok=True)
            for f in source_dir.rglob("*"):
                if f.is_file():
                    target = alias_dir / f.relative_to(source_dir)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target)

        if source_sql_dir.exists():
            alias_sql_dir.mkdir(parents=True, exist_ok=True)
            for f in source_sql_dir.rglob("*"):
                if f.is_file():
                    target = alias_sql_dir / f.relative_to(source_sql_dir)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target)

        if source_viz_dir.exists():
            alias_viz_dir.mkdir(parents=True, exist_ok=True)
            for f in source_viz_dir.rglob("*"):
                if f.is_file():
                    target = alias_viz_dir / f.relative_to(source_viz_dir)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target)

        print(f"  [OK] Created alias directory: {alias}")


def export_frontend_dashboard_assets() -> dict[str, Any]:
    """Sync dashboard-ready JSON and images into the Next.js public folder."""
    print("Exporting frontend dashboard assets...")
    ensure_frontend_dirs()

    dataset_entries, sql_analysis_assets = export_dataset_jsons()
    visualization_assets = [
        asset
        for dataset in DATASET_CONFIGS
        for asset in copy_visualizations(dataset["id"])
    ]

    for config in DATASET_CONFIGS:
        aliases = config.get("aliases", [])
        if aliases:
            copy_to_alias_dirs(config["id"], aliases)

    manifest = {
        "defaultDatasetId": dataset_entries[0]["id"] if dataset_entries else "",
        "datasets": dataset_entries,
        "sqlAnalysis": sql_analysis_assets,
        "visualizations": visualization_assets,
    }
    manifest_path = FRONTEND_DATA_DIR / "dataset-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Frontend dashboard assets exported successfully")
    print(f"Public data directory: {FRONTEND_DATA_DIR.resolve()}")
    return {"manifest": manifest_path}


if __name__ == "__main__":
    # Fixed: Dashboard data export to populate frontend
    export_frontend_dashboard_assets()
