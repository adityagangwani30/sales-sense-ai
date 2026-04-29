from __future__ import annotations

from fastapi import APIRouter, Query

from backend.database import get_connection
from backend.services.analytics_service import (
    get_category_performance,
    get_customer_segmentation,
    get_inactive_customers,
    get_insights,
    get_metrics,
    get_repeat_purchase_rate,
    get_revenue_trend,
    get_top_products,
)
from backend.services.dataset_service import validate_dataset


router = APIRouter(tags=["analytics"])


@router.get("/metrics")
def metrics(dataset: str = Query(...)) -> dict:
    dataset_name = validate_dataset(dataset)
    with get_connection() as connection:
        return get_metrics(connection, dataset_name)


@router.get("/revenue-trend")
def revenue_trend(dataset: str = Query(...)) -> dict:
    dataset_name = validate_dataset(dataset)
    with get_connection() as connection:
        return {"dataset": dataset_name, "revenue_trend": get_revenue_trend(connection, dataset_name)}


@router.get("/top-products")
def top_products(dataset: str = Query(...)) -> dict:
    dataset_name = validate_dataset(dataset)
    with get_connection() as connection:
        return {"dataset": dataset_name, "top_products": get_top_products(connection, dataset_name)}


@router.get("/customer-segmentation")
def customer_segmentation(dataset: str = Query(...)) -> dict:
    dataset_name = validate_dataset(dataset)
    with get_connection() as connection:
        return {
            "dataset": dataset_name,
            "customer_segmentation": get_customer_segmentation(connection, dataset_name),
        }


@router.get("/category-performance")
def category_performance(dataset: str = Query(...)) -> dict:
    dataset_name = validate_dataset(dataset)
    with get_connection() as connection:
        return {
            "dataset": dataset_name,
            "category_performance": get_category_performance(connection, dataset_name),
        }


@router.get("/repeat-rate")
def repeat_rate(dataset: str = Query(...)) -> dict:
    dataset_name = validate_dataset(dataset)
    with get_connection() as connection:
        return {"dataset": dataset_name, **get_repeat_purchase_rate(connection, dataset_name)}


@router.get("/inactive-customers")
def inactive_customers(dataset: str = Query(...)) -> dict:
    dataset_name = validate_dataset(dataset)
    with get_connection() as connection:
        return {
            "dataset": dataset_name,
            "inactive_customers": get_inactive_customers(connection, dataset_name),
        }


@router.get("/insights")
def insights(dataset: str = Query(...)) -> dict:
    dataset_name = validate_dataset(dataset)
    with get_connection() as connection:
        return get_insights(connection, dataset_name)
