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
        "label": "Dataset 1",
        "description": "Global E-Commerce Sales",
        "source_path": OUTPUTS_DIR / "dataset_1" / "dataset_1_cleaned.csv",
    },
    {
        "id": "dataset_2",
        "label": "Dataset 2",
        "description": "Retail Supply Chain Sales",
        "source_path": OUTPUTS_DIR / "dataset_2" / "dataset_2_cleaned.csv",
    },
]

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


def get_dataset_output_dir(dataset_id: str) -> Path:
    return OUTPUTS_DIR / dataset_id


def get_sql_output_dir(dataset_id: str) -> Path:
    return get_dataset_output_dir(dataset_id) / "sql_analysis"


def get_visualization_output_dir(dataset_id: str) -> Path:
    return get_dataset_output_dir(dataset_id) / "visualizations"


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
        raise FileNotFoundError(f"Visualization output folder not found: {visualization_dir}")

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


def export_sql_analysis_json(dataset_id: str) -> dict[str, str]:
    """Publish every SQL analysis CSV as frontend-friendly JSON."""
    sql_output_dir = get_sql_output_dir(dataset_id)
    if not sql_output_dir.exists():
        raise FileNotFoundError(f"SQL output folder not found: {sql_output_dir}")

    target_dir = FRONTEND_SQL_DIR / dataset_id
    target_dir.mkdir(parents=True, exist_ok=True)

    exported_files: dict[str, str] = {}
    for csv_path in sorted(sql_output_dir.glob("*.csv")):
        frame = pd.read_csv(csv_path)
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
        if (
            not config["source_path"].exists()
            or not get_sql_output_dir(config["id"]).exists()
            or not get_visualization_output_dir(config["id"]).exists()
        ):
            continue

        visualizations = copy_visualizations(config["id"])
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
        dataset_entries.append(
            {
                "id": config["id"],
                "label": config["label"],
                "description": config["description"],
                "dataPath": f"/data/datasets/{config['id']}.json",
            }
        )
    return dataset_entries, sql_analysis_entries


def export_frontend_dashboard_assets() -> dict[str, Any]:
    """Sync dashboard-ready JSON and images into the Next.js public folder."""
    print("Exporting frontend dashboard assets...")
    ensure_frontend_dirs()

    dataset_entries, sql_analysis_assets = export_dataset_jsons()
    visualization_assets = [
        asset
        for dataset in DATASET_CONFIGS
        if (FRONTEND_VISUALIZATION_DIR / dataset["id"]).exists()
        for asset in copy_visualizations(dataset["id"])
    ]

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
    export_frontend_dashboard_assets()
