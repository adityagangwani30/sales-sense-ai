from __future__ import annotations

from typing import Any

import pandas as pd

from backend.services.dataset_service import validate_dataset


# Every query stays pinned to one validated dataset so shared tables never mix rows
# from different sources. The source column is the isolation boundary.
def _execute_query(connection, query: str, params: tuple[Any, ...]) -> pd.DataFrame:
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []
        return pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    normalized = df.copy().where(pd.notna(df), None)
    return normalized.to_dict(orient="records")


def get_metrics(connection, dataset: str) -> dict[str, Any]:
    dataset_name = validate_dataset(dataset)
    query = """
        SELECT
            ROUND(COALESCE(SUM(f.revenue), 0), 2) AS total_revenue,
            COUNT(DISTINCT f.order_id) AS total_orders,
            COUNT(DISTINCT f.customer_id) AS total_customers,
            ROUND(COALESCE(SUM(f.revenue), 0) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS avg_order_value
        FROM fact_sales AS f
        WHERE f.source = %s
    """
    frame = _execute_query(connection, query, (dataset_name,))
    if frame.empty:
        return {
            "dataset": dataset_name,
            "total_revenue": 0.0,
            "total_orders": 0,
            "total_customers": 0,
            "avg_order_value": 0.0,
        }

    row = frame.iloc[0].to_dict()
    row["dataset"] = dataset_name
    row["avg_order_value"] = float(row.get("avg_order_value") or 0.0)
    row["total_revenue"] = float(row.get("total_revenue") or 0.0)
    row["total_orders"] = int(row.get("total_orders") or 0)
    row["total_customers"] = int(row.get("total_customers") or 0)
    return row


def get_revenue_trend(connection, dataset: str) -> list[dict[str, Any]]:
    dataset_name = validate_dataset(dataset)
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
    frame = _execute_query(connection, query, (dataset_name,))
    return _records(frame)


def get_top_products(connection, dataset: str) -> list[dict[str, Any]]:
    dataset_name = validate_dataset(dataset)
    query = """
        WITH dataset_products AS (
            SELECT product_id, product_name, category
            FROM products
            WHERE source = %s
        ),
        dataset_sales AS (
            SELECT product_id, order_id, revenue
            FROM fact_sales
            WHERE source = %s
        )
        SELECT
            p.product_id AS product_id,
            p.product_name AS product_name,
            p.category AS category,
            COUNT(DISTINCT s.order_id) AS order_count,
            ROUND(SUM(s.revenue), 2) AS total_revenue,
            ROUND(AVG(s.revenue), 2) AS avg_order_revenue
        FROM dataset_products AS p
        INNER JOIN dataset_sales AS s
            ON s.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue DESC, order_count DESC, p.product_name
        LIMIT 10
    """
    frame = _execute_query(connection, query, (dataset_name, dataset_name))
    return _records(frame)


def get_customer_segmentation(connection, dataset: str) -> list[dict[str, Any]]:
    dataset_name = validate_dataset(dataset)
    query = """
        WITH dataset_customers AS (
            SELECT customer_id, customer_name, segment, region, city
            FROM customers
            WHERE source = %s
        ),
        dataset_orders AS (
            SELECT order_id, customer_id, order_date
            FROM orders
            WHERE source = %s
        ),
        dataset_sales AS (
            SELECT order_id, revenue
            FROM fact_sales
            WHERE source = %s
        )
        SELECT
            c.customer_id AS customer_id,
            c.customer_name AS customer_name,
            c.segment AS segment,
            c.region AS region,
            c.city AS city,
            COUNT(DISTINCT o.order_id) AS order_count,
            ROUND(COALESCE(SUM(s.revenue), 0), 2) AS total_spent,
            ROUND(COALESCE(SUM(s.revenue), 0) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS avg_order_value,
            MAX(o.order_date) AS last_purchase_date
        FROM dataset_customers AS c
        LEFT JOIN dataset_orders AS o
            ON o.customer_id = c.customer_id
        LEFT JOIN dataset_sales AS s
            ON s.order_id = o.order_id
        GROUP BY c.customer_id, c.customer_name, c.segment, c.region, c.city
        ORDER BY total_spent DESC, order_count DESC, c.customer_name
    """
    frame = _execute_query(connection, query, (dataset_name, dataset_name, dataset_name))
    return _records(frame)


def get_category_performance(connection, dataset: str) -> list[dict[str, Any]]:
    dataset_name = validate_dataset(dataset)
    query = """
        WITH dataset_products AS (
            SELECT product_id, product_name, category
            FROM products
            WHERE source = %s
        ),
        dataset_sales AS (
            SELECT product_id, order_id, revenue
            FROM fact_sales
            WHERE source = %s
        )
        SELECT
            p.category AS category,
            COUNT(DISTINCT p.product_id) AS product_count,
            COUNT(DISTINCT s.order_id) AS order_count,
            ROUND(SUM(s.revenue), 2) AS total_revenue,
            ROUND(AVG(s.revenue), 2) AS avg_revenue_per_order,
            ROUND(SUM(s.revenue) / NULLIF(COUNT(DISTINCT p.product_id), 0), 2) AS revenue_per_product
        FROM dataset_products AS p
        LEFT JOIN dataset_sales AS s
            ON s.product_id = p.product_id
        GROUP BY p.category
        HAVING SUM(s.revenue) IS NOT NULL
        ORDER BY total_revenue DESC, p.category
    """
    frame = _execute_query(connection, query, (dataset_name, dataset_name))
    return _records(frame)


def get_repeat_purchase_rate(connection, dataset: str) -> dict[str, Any]:
    dataset_name = validate_dataset(dataset)
    query = """
        WITH dataset_customers AS (
            SELECT customer_id
            FROM customers
            WHERE source = %s
        ),
        dataset_orders AS (
            SELECT order_id, customer_id
            FROM orders
            WHERE source = %s
        )
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
            FROM dataset_customers AS c
            LEFT JOIN dataset_orders AS o
                ON o.customer_id = c.customer_id
            GROUP BY c.customer_id
        ) AS customer_orders
    """
    frame = _execute_query(connection, query, (dataset_name, dataset_name))
    if frame.empty:
        return {"dataset": dataset_name, "total_customers": 0, "repeat_customers": 0, "repeat_purchase_rate_pct": 0.0}

    row = frame.iloc[0].to_dict()
    row["dataset"] = dataset_name
    row["total_customers"] = int(row.get("total_customers") or 0)
    row["repeat_customers"] = int(row.get("repeat_customers") or 0)
    row["repeat_purchase_rate_pct"] = float(row.get("repeat_purchase_rate_pct") or 0.0)
    return row


def get_inactive_customers(connection, dataset: str) -> list[dict[str, Any]]:
    dataset_name = validate_dataset(dataset)
    query = """
        WITH dataset_customers AS (
            SELECT customer_id, customer_name, segment, region, city
            FROM customers
            WHERE source = %s
        ),
        dataset_orders AS (
            SELECT order_id, customer_id, order_date
            FROM orders
            WHERE source = %s
        ),
        dataset_sales AS (
            SELECT order_id, revenue
            FROM fact_sales
            WHERE source = %s
        ),
        latest_order AS (
            SELECT MAX(order_date) AS max_order_date
            FROM dataset_orders
        )
        SELECT
            c.customer_id AS customer_id,
            c.customer_name AS customer_name,
            c.segment AS segment,
            c.region AS region,
            c.city AS city,
            COUNT(DISTINCT o.order_id) AS order_count,
            ROUND(COALESCE(SUM(s.revenue), 0), 2) AS total_spent,
            MAX(o.order_date) AS last_purchase_date,
            DATEDIFF(lo.max_order_date, MAX(o.order_date)) AS days_since_last_purchase
        FROM dataset_customers AS c
        LEFT JOIN dataset_orders AS o
            ON o.customer_id = c.customer_id
        LEFT JOIN dataset_sales AS s
            ON s.order_id = o.order_id
        CROSS JOIN latest_order AS lo
        GROUP BY c.customer_id, c.customer_name, c.segment, c.region, c.city, lo.max_order_date
        HAVING MAX(o.order_date) IS NOT NULL AND DATEDIFF(lo.max_order_date, MAX(o.order_date)) > 90
        ORDER BY days_since_last_purchase DESC, total_spent DESC, c.customer_name
    """
    frame = _execute_query(connection, query, (dataset_name, dataset_name, dataset_name))
    return _records(frame)


def get_insights(connection, dataset: str) -> dict[str, Any]:
    metrics = get_metrics(connection, dataset)
    repeat_rate = get_repeat_purchase_rate(connection, dataset)
    top_products = get_top_products(connection, dataset)
    inactive_customers = get_inactive_customers(connection, dataset)

    top_product_name = top_products[0]["product_name"] if top_products else None
    inactive_count = len(inactive_customers)

    summary = (
        f"{metrics['dataset']} generated {metrics['total_revenue']:.2f} in revenue across "
        f"{metrics['total_orders']} orders with a repeat purchase rate of "
        f"{repeat_rate['repeat_purchase_rate_pct']:.2f}%."
    )

    return {
        "dataset": metrics["dataset"],
        "summary": summary,
        "top_product": top_product_name,
        "inactive_customer_count": inactive_count,
        "repeat_purchase_rate_pct": repeat_rate["repeat_purchase_rate_pct"],
    }
