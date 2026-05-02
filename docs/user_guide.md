# User Guide

This guide explains how to run SalesSense AI and how to use the dashboard once the exported data is available.

## How to Run the Project

### Backend and ML Pipeline

1. Install Python dependencies.
2. Run the main pipeline for a dataset.

```bash
pip install -r requirements.txt
python main.py --dataset dataset_1
```

You can also run the ML evaluation stage directly if the model artifacts already exist.

```bash
python ml/main.py --dataset dataset_1 --mode evaluate
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

If you regenerate pipeline outputs, refresh the frontend exports afterward.

```bash
python frontend_export.py
```

## How to Use the Dashboard

The dashboard is a static Next.js app that reads exported JSON files from `frontend/public/data/`.

- The Home page provides a quick product overview and headline KPIs.
- The Dashboard page shows charts, model metrics, ROI analysis, and SQL-driven summaries.
- The About page explains the platform and its results in a more presentation-friendly format.

## How to Switch Datasets

Use the dataset selector in the dashboard to move between the exported dataset snapshots.

- `dataset_1` represents Global E-Commerce Sales.
- `dataset_2` represents Retail Supply Chain Sales.

Each switch reloads the dataset-specific metrics, charts, and report assets.

## What Each Main Section Means

- KPI cards: high-level performance numbers such as revenue, orders, customers, and average order value.
- SQL Analytics: relational summaries built from MySQL-exported analysis files.
- ML Model Performance: comparison of regression models and their metrics.
- Predictions: confidence intervals and predicted value ranges.
- Feature Importance: most influential features for the current dataset.
- Business Insights: human-readable findings generated from the pipeline.
- ROI / Impact: estimated savings, implementation cost, and return on investment.

## Recommended Workflow

1. Run the Python pipeline for the selected dataset.
2. Export the frontend assets.
3. Start the frontend.
4. Open the dashboard and review the dataset-specific outputs.

This workflow ensures the dashboard always reflects the most recent exported artifacts.