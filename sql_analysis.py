from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd

from database_loader import connect_db


OUTPUT_ROOT_DIR = Path("outputs")


def get_sql_output_dir(dataset_name: str) -> Path:
    """Return the SQL output directory for one dataset."""
    return OUTPUT_ROOT_DIR / dataset_name / "sql_analysis"


def execute_query(conn, query: str, params: tuple | None = None) -> pd.DataFrame:
    """Run a SQL query and return the result as a pandas DataFrame."""
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []
        return pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()


def save_result(df: pd.DataFrame, dataset_name: str, filename: str) -> Path:
    """Persist one analysis result so reporting can reuse it later."""
    sql_output_dir = get_sql_output_dir(dataset_name)
    sql_output_dir.mkdir(parents=True, exist_ok=True)
    output_path = sql_output_dir / filename
    df.to_csv(output_path, index=False)
    return output_path


def get_overall_metrics(conn, dataset_name: str) -> pd.DataFrame:
    """Summarize the core health of the business in one row."""
    # Business meaning:
    # - Revenue shows total money generated.
    # - Orders and customers show scale of activity.
    # - Average order value shows the typical revenue captured per order.
    # SQL concepts used:
    # - SELECT for explicit metrics only.
    # - Aggregates (SUM, COUNT) to roll the fact table up into KPIs.
    query = """
        SELECT
            ROUND(SUM(f.revenue), 2) AS total_revenue,
            COUNT(DISTINCT f.order_id) AS total_orders,
            COUNT(DISTINCT f.customer_id) AS total_customers,
            ROUND(SUM(f.revenue) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS average_order_value
        FROM fact_sales AS f
        WHERE f.source = %s
    """
    return execute_query(conn, query, (dataset_name,))


def get_monthly_revenue_trend(conn, dataset_name: str) -> pd.DataFrame:
    """Track revenue over time at the month level."""
    # Business meaning:
    # - This trend shows seasonality and whether the business is growing month to month.
    # SQL concepts used:
    # - GROUP BY to aggregate monthly totals.
    # - ORDER BY to keep the time series in chronological order.
    # Note:
    # - The schema stores month and year separately, so both are grouped to avoid
    #   combining the same month across different years.
    query = """
        SELECT
            f.year AS year,
            f.month AS month,
            STR_TO_DATE(CONCAT(f.year, '-', LPAD(f.month, 2, '0'), '-01'), '%Y-%m-%d') AS month_start,
            ROUND(SUM(f.revenue), 2) AS monthly_revenue
        FROM fact_sales AS f
        WHERE f.source = %s
        GROUP BY f.year, f.month
        ORDER BY f.year, f.month
    """
    return execute_query(conn, query, (dataset_name,))


def get_top_products(conn, dataset_name: str) -> pd.DataFrame:
    """Return the highest revenue products for merchandising decisions."""
    # Business meaning:
    # - Helps identify best sellers and products that deserve promotion or inventory focus.
    # SQL concepts used:
    # - INNER JOIN to enrich fact rows with product attributes.
    # - GROUP BY to total product revenue.
    # - ORDER BY + LIMIT to keep only the top performers.
    query = """
        SELECT
            p.product_id AS product_id,
            p.product_name AS product_name,
            p.category AS category,
            COUNT(DISTINCT f.order_id) AS order_count,
            ROUND(SUM(f.revenue), 2) AS total_revenue,
            ROUND(AVG(f.revenue), 2) AS avg_order_revenue
        FROM fact_sales AS f
        INNER JOIN products AS p
            ON p.product_id = f.product_id
        WHERE f.source = %s
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue DESC, order_count DESC, p.product_name
        LIMIT 10
    """
    return execute_query(conn, query, (dataset_name,))


def get_customer_segmentation(conn, dataset_name: str) -> pd.DataFrame:
    """Profile each customer based on purchasing behavior."""
    # Business meaning:
    # - Identifies high-value, frequent, and recently active customers for retention campaigns.
    # SQL concepts used:
    # - LEFT JOIN keeps the customer dimension as the driving table.
    # - GROUP BY rolls order-level activity into customer segments.
    query = """
        SELECT
            c.customer_id AS customer_id,
            c.customer_name AS customer_name,
            c.segment AS segment,
            c.region AS region,
            c.city AS city,
            COUNT(DISTINCT o.order_id) AS order_count,
            ROUND(COALESCE(SUM(f.revenue), 0), 2) AS total_spent,
            ROUND(COALESCE(SUM(f.revenue), 0) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS avg_order_value,
            MAX(o.order_date) AS last_purchase_date
        FROM customers AS c
        LEFT JOIN orders AS o
            ON o.customer_id = c.customer_id
           AND o.source = %s
        LEFT JOIN fact_sales AS f
            ON f.order_id = o.order_id
           AND f.source = %s
        GROUP BY c.customer_id, c.customer_name, c.segment, c.region, c.city
        ORDER BY total_spent DESC, order_count DESC, c.customer_name
    """
    return execute_query(conn, query, (dataset_name, dataset_name))


def get_category_performance(conn, dataset_name: str) -> pd.DataFrame:
    """Compare how product categories contribute to revenue."""
    # Business meaning:
    # - Shows which categories drive the business and how broad or concentrated they are.
    # SQL concepts used:
    # - LEFT JOIN retains categories even if they have little activity.
    # - GROUP BY creates one row per category.
    # - HAVING filters out categories with no revenue after aggregation.
    query = """
        SELECT
            p.category AS category,
            COUNT(DISTINCT p.product_id) AS product_count,
            COUNT(DISTINCT f.order_id) AS order_count,
            ROUND(SUM(f.revenue), 2) AS total_revenue,
            ROUND(AVG(f.revenue), 2) AS avg_revenue_per_order,
            ROUND(SUM(f.revenue) / NULLIF(COUNT(DISTINCT p.product_id), 0), 2) AS revenue_per_product
        FROM products AS p
        LEFT JOIN fact_sales AS f
            ON f.product_id = p.product_id
           AND f.source = %s
        GROUP BY p.category
        HAVING SUM(f.revenue) IS NOT NULL
        ORDER BY total_revenue DESC, p.category
    """
    return execute_query(conn, query, (dataset_name,))


def get_repeat_purchase_rate(conn, dataset_name: str) -> pd.DataFrame:
    """Measure how many customers return to buy again."""
    # Business meaning:
    # - Repeat rate is a quick retention KPI and a signal of customer loyalty.
    # SQL concepts used:
    # - A grouped subquery calculates order frequency per customer.
    # - Outer aggregates convert that into a portfolio-level percentage.
    query = """
        SELECT
            COUNT(*) AS total_customers,
            SUM(CASE WHEN customer_orders.order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
            ROUND(
                100.0 * SUM(CASE WHEN customer_orders.order_count > 1 THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0),
                2
            ) AS repeat_purchase_rate_pct
        FROM (
            SELECT
                c.customer_id AS customer_id,
                COUNT(DISTINCT o.order_id) AS order_count
            FROM customers AS c
            LEFT JOIN orders AS o
                ON o.customer_id = c.customer_id
               AND o.source = %s
            GROUP BY c.customer_id
        ) AS customer_orders
    """
    return execute_query(conn, query, (dataset_name,))


def get_inactive_customers(conn, dataset_name: str) -> pd.DataFrame:
    """Find customers whose latest purchase is older than 90 days."""
    # Business meaning:
    # - These customers are churn-risk candidates for win-back campaigns.
    # SQL concepts used:
    # - LEFT JOIN keeps all customers in scope.
    # - HAVING filters on aggregated last_purchase_date.
    # Note:
    # - The 90-day comparison is anchored to the latest order date in the dataset so
    #   historical training data still produces meaningful churn analysis.
    query = """
        WITH latest_order AS (
            SELECT MAX(o.order_date) AS max_order_date
            FROM orders AS o
            WHERE o.source = %s
        )
        SELECT
            c.customer_id AS customer_id,
            c.customer_name AS customer_name,
            c.segment AS segment,
            c.region AS region,
            c.city AS city,
            MAX(o.order_date) AS last_purchase_date,
            DATEDIFF(lo.max_order_date, MAX(o.order_date)) AS days_since_last_purchase
        FROM customers AS c
        LEFT JOIN orders AS o
            ON o.customer_id = c.customer_id
           AND o.source = %s
        CROSS JOIN latest_order AS lo
        GROUP BY c.customer_id, c.customer_name, c.segment, c.region, c.city, lo.max_order_date
        HAVING MAX(o.order_date) IS NULL
            OR DATEDIFF(lo.max_order_date, MAX(o.order_date)) > 90
        ORDER BY days_since_last_purchase DESC, last_purchase_date
    """
    return execute_query(conn, query, (dataset_name, dataset_name))


def get_product_ranking(conn, dataset_name: str) -> pd.DataFrame:
    """Rank products inside each category by revenue."""
    # Business meaning:
    # - Shows category leaders without forcing categories to compete against each other.
    # SQL concepts used:
    # - A grouped CTE produces product revenue.
    # - RANK() is the window function used to rank products within category partitions.
    query = """
        WITH product_revenue AS (
            SELECT
                p.category AS category,
                p.product_id AS product_id,
                p.product_name AS product_name,
                COUNT(DISTINCT f.order_id) AS order_count,
                ROUND(SUM(f.revenue), 2) AS total_revenue
            FROM products AS p
            INNER JOIN fact_sales AS f
                ON f.product_id = p.product_id
               AND f.source = %s
            GROUP BY p.category, p.product_id, p.product_name
        )
        SELECT
            pr.category AS category,
            pr.product_id AS product_id,
            pr.product_name AS product_name,
            pr.order_count AS order_count,
            pr.total_revenue AS total_revenue,
            RANK() OVER (
                PARTITION BY pr.category
                ORDER BY pr.total_revenue DESC
            ) AS revenue_rank
        FROM product_revenue AS pr
        ORDER BY pr.category, revenue_rank, pr.product_name
    """
    return execute_query(conn, query, (dataset_name,))


def get_revenue_growth(conn, dataset_name: str) -> pd.DataFrame:
    """Calculate month-over-month revenue change."""
    # Business meaning:
    # - Makes it easy to see acceleration, slowdown, and inflection points in revenue.
    # SQL concepts used:
    # - GROUP BY creates monthly totals.
    # - LAG() brings in the previous month so growth can be computed in SQL.
    query = """
        WITH monthly_revenue AS (
            SELECT
                f.year AS year,
                f.month AS month,
                STR_TO_DATE(CONCAT(f.year, '-', LPAD(f.month, 2, '0'), '-01'), '%Y-%m-%d') AS month_start,
                ROUND(SUM(f.revenue), 2) AS monthly_revenue
            FROM fact_sales AS f
            WHERE f.source = %s
            GROUP BY f.year, f.month
        ),
        revenue_with_lag AS (
            SELECT
                mr.year AS year,
                mr.month AS month,
                mr.month_start AS month_start,
                mr.monthly_revenue AS monthly_revenue,
                LAG(mr.monthly_revenue) OVER (ORDER BY mr.month_start) AS previous_month_revenue
            FROM monthly_revenue AS mr
        )
        SELECT
            rwl.year AS year,
            rwl.month AS month,
            rwl.month_start AS month_start,
            rwl.monthly_revenue AS monthly_revenue,
            rwl.previous_month_revenue AS previous_month_revenue,
            ROUND(rwl.monthly_revenue - rwl.previous_month_revenue, 2) AS revenue_change,
            ROUND(
                100.0 * (rwl.monthly_revenue - rwl.previous_month_revenue)
                / NULLIF(rwl.previous_month_revenue, 0),
                2
            ) AS revenue_growth_pct
        FROM revenue_with_lag AS rwl
        ORDER BY rwl.month_start
    """
    return execute_query(conn, query, (dataset_name,))


def get_customer_lifetime_value(conn, dataset_name: str) -> pd.DataFrame:
    """Return the top customers by lifetime revenue contribution."""
    # Business meaning:
    # - CLV highlights the customers who create the most long-term value.
    # SQL concepts used:
    # - INNER JOIN combines customers, orders, and facts.
    # - MIN/MAX measure the customer lifespan.
    # - ROW_NUMBER() creates an ordered leaderboard of the highest-value customers.
    # - ORDER BY + LIMIT returns the top 20 most valuable customers.
    query = """
        WITH customer_value AS (
            SELECT
                c.customer_id AS customer_id,
                c.customer_name AS customer_name,
                c.segment AS segment,
                c.region AS region,
                COUNT(DISTINCT o.order_id) AS order_count,
                ROUND(SUM(f.revenue), 2) AS lifetime_value,
                MIN(o.order_date) AS first_order_date,
                MAX(o.order_date) AS last_order_date,
                DATEDIFF(MAX(o.order_date), MIN(o.order_date)) AS lifespan_days
            FROM customers AS c
            INNER JOIN orders AS o
                ON o.customer_id = c.customer_id
               AND o.source = %s
            INNER JOIN fact_sales AS f
                ON f.order_id = o.order_id
               AND f.source = %s
            GROUP BY c.customer_id, c.customer_name, c.segment, c.region
        )
        SELECT
            ROW_NUMBER() OVER (
                ORDER BY cv.lifetime_value DESC, cv.order_count DESC, cv.customer_name
            ) AS customer_rank,
            cv.customer_id AS customer_id,
            cv.customer_name AS customer_name,
            cv.segment AS segment,
            cv.region AS region,
            cv.order_count AS order_count,
            cv.lifetime_value AS lifetime_value,
            cv.first_order_date AS first_order_date,
            cv.last_order_date AS last_order_date,
            cv.lifespan_days AS lifespan_days
        FROM customer_value AS cv
        ORDER BY customer_rank
        LIMIT 20
    """
    return execute_query(conn, query, (dataset_name, dataset_name))


def get_regional_performance(conn, dataset_name: str) -> pd.DataFrame:
    """Bonus analysis for comparing revenue concentration by geography."""
    # Business meaning:
    # - Regional performance helps identify where demand is strongest and where expansion
    #   or localized promotions may be most effective.
    # SQL concepts used:
    # - INNER JOIN enriches fact data with geography from the customer dimension.
    # - GROUP BY creates a region-level summary.
    query = """
        SELECT
            c.region AS region,
            c.city AS city,
            COUNT(DISTINCT f.order_id) AS order_count,
            COUNT(DISTINCT f.customer_id) AS customer_count,
            ROUND(SUM(f.revenue), 2) AS total_revenue,
            ROUND(AVG(f.revenue), 2) AS avg_order_revenue
        FROM fact_sales AS f
        INNER JOIN customers AS c
            ON c.customer_id = f.customer_id
        WHERE f.source = %s
        GROUP BY c.region, c.city
        ORDER BY total_revenue DESC, order_count DESC, c.region, c.city
    """
    return execute_query(conn, query, (dataset_name,))


def run_sql_analysis(
    dataset_name: str,
    host: str | None = None,
    user: str | None = None,
    password: str | None = None,
    database: str | None = None,
    port: int | None = None,
) -> dict[str, Path]:
    """Run all Week 4 SQL analyses and save each one as a CSV file."""
    print(f"Running SQL Analysis for {dataset_name}...")

    analyses: list[tuple[str, str, Callable[[object, str], pd.DataFrame], str]] = [
        ("overall_metrics", "Overall metrics extracted", get_overall_metrics, "overall_metrics.csv"),
        ("monthly_revenue_trend", "Monthly revenue trend extracted", get_monthly_revenue_trend, "monthly_revenue_trend.csv"),
        ("top_products", "Top products extracted", get_top_products, "top_products.csv"),
        ("customer_segmentation", "Customer segmentation completed", get_customer_segmentation, "customer_segmentation.csv"),
        ("category_performance", "Category performance extracted", get_category_performance, "category_performance.csv"),
        ("repeat_purchase_rate", "Repeat purchase rate calculated", get_repeat_purchase_rate, "repeat_purchase_rate.csv"),
        ("inactive_customers", "Inactive customers extracted", get_inactive_customers, "inactive_customers.csv"),
        ("product_ranking", "Product ranking extracted", get_product_ranking, "product_ranking.csv"),
        ("revenue_growth", "Revenue growth trend extracted", get_revenue_growth, "revenue_growth.csv"),
        ("customer_lifetime_value", "Customer lifetime value extracted", get_customer_lifetime_value, "customer_lifetime_value.csv"),
        ("regional_performance", "Regional performance extracted", get_regional_performance, "regional_performance.csv"),
    ]

    conn = connect_db(host=host, user=user, password=password, database=database, port=port)
    output_files: dict[str, Path] = {}

    try:
        for analysis_name, log_message, analysis_func, filename in analyses:
            df = analysis_func(conn, dataset_name)
            output_files[analysis_name] = save_result(df, dataset_name, filename)
            print(log_message)
        print(f"SQL analysis outputs saved to: {get_sql_output_dir(dataset_name).resolve()}")
        return output_files
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit("Run sql_analysis.run_sql_analysis(dataset_name=...) from the pipeline.")
