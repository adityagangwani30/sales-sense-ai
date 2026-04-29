from __future__ import annotations

from pathlib import Path
from textwrap import shorten

import numpy as np
import pandas as pd
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator


OUTPUT_ROOT_DIR = Path("outputs")

PRIMARY_COLOR = "#2E86AB"
SECONDARY_COLOR = "#A23B72"
POSITIVE_COLOR = "#06A77D"
NEGATIVE_COLOR = "#D62246"
ACCENT_COLOR = "#F4B942"
NEUTRAL_COLOR = "#6C757D"
CHART_COLORS = [
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    POSITIVE_COLOR,
    ACCENT_COLOR,
    "#5C80BC",
    "#7A9E9F",
    NEUTRAL_COLOR,
]

CURRENCY_FORMATTER = FuncFormatter(
    lambda value, _: f"${value / 1000:,.0f}K" if abs(value) >= 1000 else f"${value:,.0f}"
)


def configure_plot_style() -> None:
    """Apply one consistent visual language across every chart."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#D9E2EC",
            "axes.labelcolor": "#243B53",
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "xtick.color": "#486581",
            "ytick.color": "#486581",
            "grid.color": "#BCCCDC",
            "grid.alpha": 0.3,
            "grid.linestyle": "--",
            "legend.frameon": False,
            "font.size": 10,
        }
    )


def get_dataset_output_dir(dataset_name: str) -> Path:
    """Return the root output directory for one dataset."""
    return OUTPUT_ROOT_DIR / dataset_name


def get_sql_output_dir(dataset_name: str) -> Path:
    """Return the SQL analysis directory for one dataset."""
    return get_dataset_output_dir(dataset_name) / "sql_analysis"


def get_visualization_output_dir(dataset_name: str) -> Path:
    """Return the visualization directory for one dataset."""
    return get_dataset_output_dir(dataset_name) / "visualizations"


def get_cleaned_output_path(dataset_name: str) -> Path:
    """Return the cleaned CSV path for one dataset."""
    return get_dataset_output_dir(dataset_name) / f"{dataset_name}_cleaned.csv"


def ensure_output_dir(dataset_name: str) -> Path:
    """Create the visualization folder if it does not exist yet."""
    visualization_output_dir = get_visualization_output_dir(dataset_name)
    visualization_output_dir.mkdir(parents=True, exist_ok=True)
    return visualization_output_dir


def load_sql_output(dataset_name: str, filename: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    """Load one SQL analysis export from disk."""
    csv_path = get_sql_output_dir(dataset_name) / filename
    if not csv_path.exists():
        raise FileNotFoundError(f"Required SQL output not found: {csv_path}")
    return pd.read_csv(csv_path, parse_dates=parse_dates)


def load_cleaned_output(dataset_name: str) -> pd.DataFrame:
    """Load the cleaned dataset for one isolated visualization run."""
    cleaned_path = get_cleaned_output_path(dataset_name)
    if not cleaned_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {cleaned_path}")

    cleaned_df = pd.read_csv(cleaned_path, parse_dates=["date"], low_memory=False)
    for column_name in ("sales", "price", "quantity", "revenue"):
        if column_name in cleaned_df.columns:
            cleaned_df[column_name] = pd.to_numeric(cleaned_df[column_name], errors="coerce")
    return cleaned_df


def save_figure(fig: plt.Figure, dataset_name: str, filename: str) -> Path:
    """Save one figure as a high-resolution PNG."""
    output_dir = ensure_output_dir(dataset_name)
    output_path = output_dir / filename
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def add_light_grid(ax: plt.Axes, axis: str = "y") -> None:
    """Use a subtle grid so values are readable without clutter."""
    ax.grid(True, axis=axis, alpha=0.3)


def draw_no_data(ax: plt.Axes, title: str, x_label: str, y_label: str) -> None:
    """Render a consistent placeholder when an input dataframe has no usable rows."""
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.text(
        0.5,
        0.5,
        "No data available",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=11,
        color=NEUTRAL_COLOR,
    )
    ax.grid(False)


def add_bar_labels(ax: plt.Axes, horizontal: bool = False, currency: bool = False) -> None:
    """Add value labels so the audience can read exact values at a glance."""
    for patch in ax.patches:
        if horizontal:
            value = patch.get_width()
            x_position = value + max(value * 0.01, 5)
            y_position = patch.get_y() + patch.get_height() / 2
            label = f"${value:,.0f}" if currency else f"{value:,.0f}"
            ax.text(x_position, y_position, label, va="center", ha="left", fontsize=9, color="#243B53")
        else:
            value = patch.get_height()
            x_position = patch.get_x() + patch.get_width() / 2
            y_position = value + max(value * 0.01, 1)
            label = f"${value:,.0f}" if currency else f"{value:,.0f}"
            ax.text(x_position, y_position, label, va="bottom", ha="center", fontsize=9, color="#243B53")


def abbreviate_labels(labels: pd.Series, max_width: int = 28) -> list[str]:
    """Shorten long product names so chart labels stay readable."""
    return [shorten(str(label), width=max_width, placeholder="...") for label in labels]


def prepare_category_distribution(category_df: pd.DataFrame, max_categories: int = 6) -> pd.DataFrame:
    """Limit the pie chart to a clean set of categories and group the tail into Other."""
    prepared = category_df.copy()
    prepared["total_revenue"] = pd.to_numeric(prepared["total_revenue"], errors="coerce")
    prepared = prepared.dropna(subset=["category", "total_revenue"]).sort_values("total_revenue", ascending=False)

    if len(prepared) <= max_categories:
        return prepared

    head = prepared.head(max_categories - 1).copy()
    other_revenue = prepared.iloc[max_categories - 1 :]["total_revenue"].sum()
    other_row = pd.DataFrame([{"category": "other", "total_revenue": other_revenue}])
    return pd.concat([head, other_row], ignore_index=True)


def build_order_values(cleaned_df: pd.DataFrame) -> pd.Series:
    """Aggregate line items into order values for a true spending distribution view."""
    value_column = "sales" if "sales" in cleaned_df.columns else "revenue"
    if value_column not in cleaned_df.columns:
        raise ValueError("The cleaned datasets do not contain a sales or revenue column.")

    if "order_id" in cleaned_df.columns and cleaned_df["order_id"].notna().any():
        order_values = cleaned_df.groupby("order_id", dropna=True)[value_column].sum()
    else:
        order_values = cleaned_df[value_column]

    order_values = pd.to_numeric(order_values, errors="coerce").dropna()
    return order_values[order_values > 0]


def plot_monthly_revenue_trend(ax: plt.Axes, monthly_revenue_df: pd.DataFrame) -> None:
    """A line chart best reveals momentum, seasonality, and peak months over time."""
    trend_df = monthly_revenue_df.copy()
    trend_df["month_start"] = pd.to_datetime(trend_df["month_start"], errors="coerce")
    trend_df["monthly_revenue"] = pd.to_numeric(trend_df["monthly_revenue"], errors="coerce")
    trend_df = trend_df.dropna(subset=["month_start", "monthly_revenue"]).sort_values("month_start")

    if trend_df.empty:
        draw_no_data(ax, "Monthly Revenue Trend", "Month", "Revenue ($)")
        return

    ax.plot(
        trend_df["month_start"],
        trend_df["monthly_revenue"],
        color=PRIMARY_COLOR,
        marker="o",
        linewidth=2.5,
        markersize=6,
    )
    ax.fill_between(
        trend_df["month_start"],
        trend_df["monthly_revenue"],
        color=PRIMARY_COLOR,
        alpha=0.12,
    )

    peak_row = trend_df.loc[trend_df["monthly_revenue"].idxmax()]
    peak_label = f"Peak: {peak_row['month_start']:%b %Y}\n${peak_row['monthly_revenue']:,.0f}"
    ax.annotate(
        peak_label,
        xy=(peak_row["month_start"], peak_row["monthly_revenue"]),
        xytext=(20, 18),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": SECONDARY_COLOR, "lw": 1.5},
        fontsize=9,
        color=SECONDARY_COLOR,
        bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": SECONDARY_COLOR, "alpha": 0.9},
    )

    starting_revenue = trend_df["monthly_revenue"].iloc[0]
    ending_revenue = trend_df["monthly_revenue"].iloc[-1]
    growth_pct = ((ending_revenue - starting_revenue) / starting_revenue * 100) if starting_revenue else 0
    ax.text(
        0.02,
        0.95,
        f"Net trend: {growth_pct:+.1f}%",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        color=POSITIVE_COLOR if growth_pct >= 0 else NEGATIVE_COLOR,
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#D9E2EC"},
    )

    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue ($)")
    ax.yaxis.set_major_formatter(CURRENCY_FORMATTER)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.tick_params(axis="x", rotation=45)
    add_light_grid(ax, axis="both")


def plot_top_products(ax: plt.Axes, top_products_df: pd.DataFrame) -> None:
    """A horizontal bar chart makes ranked product comparisons easy to scan."""
    ranked_df = top_products_df.copy()
    ranked_df["total_revenue"] = pd.to_numeric(ranked_df["total_revenue"], errors="coerce")
    ranked_df = ranked_df.dropna(subset=["product_name", "total_revenue"])
    ranked_df = ranked_df.sort_values("total_revenue", ascending=True)

    if ranked_df.empty:
        draw_no_data(ax, "Top 10 Products by Revenue", "Revenue ($)", "Product")
        return

    colors = [PRIMARY_COLOR] * len(ranked_df)
    if colors:
        colors[-1] = SECONDARY_COLOR

    ax.barh(
        abbreviate_labels(ranked_df["product_name"]),
        ranked_df["total_revenue"],
        color=colors,
        edgecolor="none",
    )
    add_bar_labels(ax, horizontal=True, currency=True)

    ax.set_title("Top 10 Products by Revenue")
    ax.set_xlabel("Revenue ($)")
    ax.set_ylabel("Product")
    ax.xaxis.set_major_formatter(CURRENCY_FORMATTER)
    add_light_grid(ax, axis="x")


def plot_category_distribution(ax: plt.Axes, category_df: pd.DataFrame) -> None:
    """A pie chart works well here because the question is share of revenue by category."""
    prepared = prepare_category_distribution(category_df)
    if prepared.empty:
        draw_no_data(ax, "Category Revenue Distribution", "", "")
        return
    largest_index = prepared["total_revenue"].idxmax()
    explode = [0.08 if index == largest_index else 0 for index in prepared.index]

    wedges, _, autotexts = ax.pie(
        prepared["total_revenue"],
        labels=prepared["category"].str.title(),
        autopct=lambda pct: f"{pct:.1f}%",
        startangle=90,
        colors=CHART_COLORS[: len(prepared)],
        explode=explode,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
        pctdistance=0.8,
    )

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(9)

    ax.set_title("Category Revenue Distribution")
    ax.axis("equal")
    ax.legend(wedges, prepared["category"].str.title(), loc="center left", bbox_to_anchor=(1.0, 0.5))


def prepare_segment_summary(customer_segmentation_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize customer segments for dashboard-level comparison."""
    summary_df = customer_segmentation_df.copy()
    summary_df["avg_order_value"] = pd.to_numeric(summary_df["avg_order_value"], errors="coerce")
    summary_df["segment"] = summary_df["segment"].fillna("unknown").astype(str).str.title()

    segment_summary = (
        summary_df.groupby("segment", as_index=False)
        .agg(
            customer_count=("customer_id", "nunique"),
            avg_order_value=("avg_order_value", "mean"),
        )
        .sort_values("customer_count", ascending=False)
    )
    return segment_summary


def plot_customer_segmentation(
    ax_count: plt.Axes,
    ax_aov: plt.Axes,
    customer_segmentation_df: pd.DataFrame,
) -> None:
    """Grouped customer summaries show both audience size and customer value by segment."""
    segment_summary = prepare_segment_summary(customer_segmentation_df)
    if segment_summary.empty:
        draw_no_data(ax_count, "Customer Count by Segment", "Segment", "Customers")
        draw_no_data(ax_aov, "Average Order Value by Segment", "Segment", "Avg Order Value ($)")
        return
    segments = segment_summary["segment"]

    ax_count.bar(segments, segment_summary["customer_count"], color=PRIMARY_COLOR, edgecolor="none")
    add_bar_labels(ax_count)
    ax_count.set_title("Customer Count by Segment")
    ax_count.set_xlabel("Segment")
    ax_count.set_ylabel("Customers")
    ax_count.yaxis.set_major_locator(MaxNLocator(integer=True))
    add_light_grid(ax_count, axis="y")

    ax_aov.bar(segments, segment_summary["avg_order_value"], color=POSITIVE_COLOR, edgecolor="none")
    add_bar_labels(ax_aov, currency=True)
    ax_aov.set_title("Average Order Value by Segment")
    ax_aov.set_xlabel("Segment")
    ax_aov.set_ylabel("Avg Order Value ($)")
    ax_aov.yaxis.set_major_formatter(CURRENCY_FORMATTER)
    add_light_grid(ax_aov, axis="y")

    for axis in (ax_count, ax_aov):
        axis.tick_params(axis="x", rotation=20)


def plot_order_value_distribution(ax: plt.Axes, cleaned_df: pd.DataFrame) -> None:
    """A histogram is ideal for spotting common spend ranges and skew in order values."""
    order_values = build_order_values(cleaned_df)
    if order_values.empty:
        draw_no_data(ax, "Order Value Distribution", "Order Value ($)", "Order Frequency")
        return
    counts, _, _ = ax.hist(
        order_values,
        bins=20,
        color=PRIMARY_COLOR,
        alpha=0.85,
        edgecolor="white",
    )

    mean_value = order_values.mean()
    median_value = order_values.median()
    distribution_note = "Right-skewed spend pattern" if mean_value > median_value * 1.1 else "Balanced spend pattern"

    ax.axvline(mean_value, color=SECONDARY_COLOR, linestyle="--", linewidth=2, label=f"Mean = ${mean_value:,.0f}")
    ax.text(
        0.02,
        0.95,
        distribution_note,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        color="#243B53",
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#D9E2EC"},
    )

    ax.set_title("Order Value Distribution")
    ax.set_xlabel("Order Value ($)")
    ax.set_ylabel("Order Frequency")
    ax.xaxis.set_major_formatter(CURRENCY_FORMATTER)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim(0, max(counts) * 1.15 if len(counts) else 1)
    ax.legend()
    add_light_grid(ax, axis="y")


def plot_price_vs_sales_scatter(ax: plt.Axes, cleaned_df: pd.DataFrame) -> None:
    """A scatter plot reveals whether higher prices are associated with larger sales values."""
    if not {"price", "sales"}.issubset(cleaned_df.columns):
        draw_no_data(ax, "Price vs Sales Correlation", "Unit Price ($)", "Sales Value ($)")
        return

    scatter_df = cleaned_df[["price", "sales"]].copy()
    scatter_df["price"] = pd.to_numeric(scatter_df["price"], errors="coerce")
    scatter_df["sales"] = pd.to_numeric(scatter_df["sales"], errors="coerce")
    scatter_df = scatter_df.dropna()
    scatter_df = scatter_df[(scatter_df["price"] > 0) & (scatter_df["sales"] > 0)]
    if len(scatter_df) < 2:
        draw_no_data(ax, "Price vs Sales Correlation", "Unit Price ($)", "Sales Value ($)")
        return

    if len(scatter_df) > 1500:
        scatter_df = scatter_df.sample(1500, random_state=42)

    ax.scatter(
        scatter_df["price"],
        scatter_df["sales"],
        s=24,
        alpha=0.4,
        color=PRIMARY_COLOR,
        edgecolors="none",
    )

    slope, intercept = np.polyfit(scatter_df["price"], scatter_df["sales"], 1)
    trend_x = np.linspace(scatter_df["price"].min(), scatter_df["price"].max(), 100)
    trend_y = slope * trend_x + intercept
    ax.plot(trend_x, trend_y, color=SECONDARY_COLOR, linewidth=2)

    correlation = scatter_df["price"].corr(scatter_df["sales"])
    ax.text(
        0.02,
        0.95,
        f"Correlation: {correlation:.2f}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        color="#243B53",
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#D9E2EC"},
    )

    ax.set_title("Price vs Sales Correlation")
    ax.set_xlabel("Unit Price ($)")
    ax.set_ylabel("Sales Value ($)")
    ax.xaxis.set_major_formatter(CURRENCY_FORMATTER)
    ax.yaxis.set_major_formatter(CURRENCY_FORMATTER)
    add_light_grid(ax, axis="both")


def create_monthly_revenue_trend(dataset_name: str, monthly_revenue_df: pd.DataFrame | None = None) -> Path:
    """Create the monthly revenue trend chart."""
    configure_plot_style()
    monthly_revenue_df = (
        monthly_revenue_df
        if monthly_revenue_df is not None
        else load_sql_output(dataset_name, "monthly_revenue_trend.csv", parse_dates=["month_start"])
    )
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_monthly_revenue_trend(ax, monthly_revenue_df)
    fig.tight_layout()
    return save_figure(fig, dataset_name, "monthly_revenue_trend.png")


def create_top_products_chart(dataset_name: str, top_products_df: pd.DataFrame | None = None) -> Path:
    """Create the ranked top products chart."""
    configure_plot_style()
    top_products_df = top_products_df if top_products_df is not None else load_sql_output(dataset_name, "top_products.csv")
    fig, ax = plt.subplots(figsize=(12, 7))
    plot_top_products(ax, top_products_df)
    fig.tight_layout()
    return save_figure(fig, dataset_name, "top_products.png")


def create_category_distribution_chart(dataset_name: str, category_df: pd.DataFrame | None = None) -> Path:
    """Create the category share chart."""
    configure_plot_style()
    category_df = category_df if category_df is not None else load_sql_output(dataset_name, "category_performance.csv")
    fig, ax = plt.subplots(figsize=(10, 7))
    plot_category_distribution(ax, category_df)
    fig.tight_layout()
    return save_figure(fig, dataset_name, "category_distribution.png")


def create_customer_segmentation_chart(dataset_name: str, customer_segmentation_df: pd.DataFrame | None = None) -> Path:
    """Create the two-panel customer segmentation figure."""
    configure_plot_style()
    customer_segmentation_df = (
        customer_segmentation_df
        if customer_segmentation_df is not None
        else load_sql_output(dataset_name, "customer_segmentation.csv")
    )
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    plot_customer_segmentation(axes[0], axes[1], customer_segmentation_df)
    fig.suptitle("Customer Segmentation Overview", fontsize=16, fontweight="bold")
    fig.tight_layout()
    return save_figure(fig, dataset_name, "customer_segmentation.png")


def create_order_value_distribution_chart(dataset_name: str, cleaned_df: pd.DataFrame | None = None) -> Path:
    """Create the order value histogram."""
    configure_plot_style()
    cleaned_df = cleaned_df if cleaned_df is not None else load_cleaned_output(dataset_name)
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_order_value_distribution(ax, cleaned_df)
    fig.tight_layout()
    return save_figure(fig, dataset_name, "order_value_distribution.png")


def create_price_vs_sales_scatter_chart(dataset_name: str, cleaned_df: pd.DataFrame | None = None) -> Path:
    """Create the optional scatter plot."""
    configure_plot_style()
    cleaned_df = cleaned_df if cleaned_df is not None else load_cleaned_output(dataset_name)
    fig, ax = plt.subplots(figsize=(11, 6))
    plot_price_vs_sales_scatter(ax, cleaned_df)
    fig.tight_layout()
    return save_figure(fig, dataset_name, "price_vs_sales_scatter.png")


def create_dashboard(
    dataset_name: str,
    monthly_revenue_df: pd.DataFrame | None = None,
    top_products_df: pd.DataFrame | None = None,
    category_df: pd.DataFrame | None = None,
    customer_segmentation_df: pd.DataFrame | None = None,
    cleaned_df: pd.DataFrame | None = None,
) -> Path:
    """Create one dashboard-style figure that combines the key business views."""
    configure_plot_style()
    monthly_revenue_df = (
        monthly_revenue_df
        if monthly_revenue_df is not None
        else load_sql_output(dataset_name, "monthly_revenue_trend.csv", parse_dates=["month_start"])
    )
    top_products_df = top_products_df if top_products_df is not None else load_sql_output(dataset_name, "top_products.csv")
    category_df = category_df if category_df is not None else load_sql_output(dataset_name, "category_performance.csv")
    customer_segmentation_df = (
        customer_segmentation_df
        if customer_segmentation_df is not None
        else load_sql_output(dataset_name, "customer_segmentation.csv")
    )
    cleaned_df = cleaned_df if cleaned_df is not None else load_cleaned_output(dataset_name)

    fig, axes = plt.subplots(3, 2, figsize=(18, 16))
    fig.suptitle("SalesSense Retail Analytics Dashboard", fontsize=20, fontweight="bold")

    plot_monthly_revenue_trend(axes[0, 0], monthly_revenue_df)
    plot_top_products(axes[0, 1], top_products_df)
    plot_category_distribution(axes[1, 0], category_df)
    plot_customer_segmentation(axes[1, 1], axes[2, 0], customer_segmentation_df)
    plot_order_value_distribution(axes[2, 1], cleaned_df)

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    return save_figure(fig, dataset_name, "sales_dashboard.png")


def run_visualizations(dataset_name: str, cleaned_df: pd.DataFrame | None = None) -> dict[str, Path]:
    """Generate all Week 5 charts from SQL outputs and cleaned transactional data."""
    print(f"Generating visualizations for {dataset_name}...")

    monthly_revenue_df = load_sql_output(dataset_name, "monthly_revenue_trend.csv", parse_dates=["month_start"])
    top_products_df = load_sql_output(dataset_name, "top_products.csv")
    category_df = load_sql_output(dataset_name, "category_performance.csv")
    customer_segmentation_df = load_sql_output(dataset_name, "customer_segmentation.csv")
    cleaned_df = cleaned_df if cleaned_df is not None else load_cleaned_output(dataset_name)

    output_files = {
        "monthly_revenue_trend": create_monthly_revenue_trend(dataset_name, monthly_revenue_df),
        "top_products": create_top_products_chart(dataset_name, top_products_df),
        "category_distribution": create_category_distribution_chart(dataset_name, category_df),
        "customer_segmentation": create_customer_segmentation_chart(dataset_name, customer_segmentation_df),
        "order_value_distribution": create_order_value_distribution_chart(dataset_name, cleaned_df),
        "price_vs_sales_scatter": create_price_vs_sales_scatter_chart(dataset_name, cleaned_df),
        "dashboard": create_dashboard(
            dataset_name=dataset_name,
            monthly_revenue_df=monthly_revenue_df,
            top_products_df=top_products_df,
            category_df=category_df,
            customer_segmentation_df=customer_segmentation_df,
            cleaned_df=cleaned_df,
        ),
    }

    print("Revenue trend created")
    print("Top products chart created")
    print("Category distribution created")
    print("Customer segmentation created")
    print("Order value distribution created")
    print("Scatter plot created")
    print("Dashboard created successfully")
    print(f"Visualization outputs saved to: {get_visualization_output_dir(dataset_name).resolve()}")
    return output_files


if __name__ == "__main__":
    raise SystemExit("Run visualization.run_visualizations(dataset_name=...) from the pipeline.")
