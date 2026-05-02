# Architecture

SalesSense AI is built as a dataset-isolated analytics pipeline that prepares data in Python, stores relational outputs in MySQL, evaluates machine learning models, and publishes static dashboard assets for the Next.js frontend.

## End-to-End Flow

1. Raw data is loaded from `original_dataset/` or from the cleaned dataset outputs.
2. The preprocessing layer standardizes columns, resolves data types, and engineers model-ready features.
3. The pipeline loads the processed data into MySQL for structured SQL analysis.
4. The ML layer trains and evaluates regression models and writes metrics, feature importance, error analysis, and ROI outputs.
5. The export layer copies JSON, CSV, plot, and report artifacts into `frontend/public/data/`.
6. The Next.js frontend reads those static files and renders the Home, Dashboard, and About pages without needing a live application server.

## Main Components

### Pipeline

The Python pipeline orchestrates preprocessing, feature engineering, model training, evaluation, and artifact export. The entry point is `main.py`, which coordinates the full run for one dataset at a time.

### Database

MySQL is used as the structured analytics layer. It supports SQL-based summaries, aggregation, and relational analysis that complement the file-based ML pipeline.

### ML Module

The ML module prepares features, splits the data into train and test sets, trains Linear Regression, Random Forest, and XGBoost models, and generates evaluation metrics plus business-facing explanations.

### Frontend

The frontend is a static Next.js application. It reads exported JSON and text assets from `frontend/public/data/` and renders interactive dashboard views with no runtime dependency on a backend API.

## Dataset Isolation

SalesSense AI keeps `dataset_1` and `dataset_2` isolated throughout the stack.

- Each dataset has its own cleaned CSV output.
- Each dataset has its own ML outputs, metrics, plots, and reports.
- Each dataset has its own frontend JSON export paths and visualization assets.
- No intermediate or final artifact is merged across datasets.

This isolation makes comparisons reliable and prevents one dataset from contaminating another during training or reporting.

## Simple Diagram

```text
Raw Dataset
	|
	v
Preprocessing + Feature Engineering
	|
	+--> MySQL tables for SQL analysis
	|
	v
ML Training and Evaluation
	|
	v
Reports / Metrics / Plots / ROI JSON
	|
	v
frontend/public/data
	|
	v
Next.js Dashboard
```

## Why This Structure Works

- It keeps the analytics flow reproducible.
- It separates computation from presentation.
- It supports offline demo usage through static exports.
- It makes each dataset traceable from raw input to final output.
