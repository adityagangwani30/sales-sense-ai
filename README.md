# SalesSense AI

> **Turn raw retail data into production-grade predictions, SQL-backed analytics, and a live dashboard — end to end, fully automated.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?logo=scikit-learn)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Regressor-red)](https://xgboost.readthedocs.io/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-blue?logo=mysql)](https://www.mysql.com/)

---

## 📖 Overview

Most retail businesses are sitting on mountains of transactional data they never fully use. Spreadsheets get emailed around, reports get built manually, and no one has a clear picture of which products, customers, or time periods actually drive revenue.

**SalesSense AI** solves this by automating the entire analytics workflow — from raw CSV/Excel files all the way to trained ML models, SQL-powered business reports, and a real-time interactive dashboard. The system processes two distinct retail datasets independently with zero data leakage between them, and produces verified, reproducible results for each.

The project currently operates on two real-world datasets:

- **`Retail_Transactions_2024`** (`global_ecommerce_sales.csv`) — Global e-commerce transaction data
- **`Market_Trend_Data_2025`** (`Retail-Supply-Chain-Sales-Dataset.xlsx`) — Retail supply chain sales data

Each dataset is run through the full pipeline independently: preprocessing → database load → SQL analytics → ML training → evaluation → dashboard export.

---

## ✨ Features

- **ML Sales Forecasting** — Three regression models (Linear Regression, Random Forest, XGBoost) trained per dataset with full evaluation
- **Revenue Trend Analysis** — Monthly and quarterly revenue breakdowns, best/worst period identification
- **Customer Segmentation** — Per-customer spend aggregation, order frequency, and weekend vs. weekday behavior analysis
- **Category & Product Performance** — Top and bottom product rankings by revenue contribution with feature-level correlation to sales
- **ROI & Business Impact Analysis** — Automated overstock/understock savings estimation with ROI calculation
- **Interactive Next.js Dashboard** — Live-rendered charts (Recharts), KPI cards, and dataset switching built with React 19, Tailwind CSS, and Radix UI
- **SQL Analytics Layer** — MySQL-backed structured analysis run after each pipeline execution
- **Dataset Isolation** — Strict separation: no data, models, or outputs are ever merged across datasets
- **5-Fold Cross-Validation** — Built-in CV with R², MAE, RMSE per fold and aggregate stats
- **Residual Diagnostics** — Error histograms, Q-Q plots, residual plots, and box plots generated per model run
- **Feature & Permutation Importance** — Dual importance analysis (model-based + permutation) with comparison output
- **Confidence Scoring** — Tree-level prediction interval estimation for Random Forest outputs

---

## 🧠 Tech Stack

### Backend / ML Pipeline

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Data Processing | pandas, NumPy, openpyxl |
| Machine Learning | scikit-learn, XGBoost |
| Statistical Analysis | SciPy |
| Visualization | Matplotlib, Seaborn |
| Database | MySQL + mysql-connector-python |
| Config & Env | python-dotenv, PyYAML |

### Frontend Dashboard

| Layer | Technology |
|---|---|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| UI Components | Radix UI (full suite) |
| Charting | Recharts 2.15 |
| Icons | Lucide React |
| WebGL Effects | OGL (Aurora background) |
| Analytics | Vercel Analytics |

### ML Models

| Model | Role | Config |
|---|---|---|
| Random Forest | **Primary model** | 300 estimators, max_depth=12, min_samples_leaf=2 |
| XGBoost | Benchmark comparison | 300 estimators, lr=0.05, max_depth=6, subsample=0.9 |
| Linear Regression | Baseline | sklearn default |

---

## ⚙️ System Architecture

```
Raw Data (CSV / Excel)
        │
        ▼
┌─────────────────────┐
│   pipeline.py       │  Column detection, normalization, outlier removal,
│   (Data Ingestion   │  missing value imputation, feature engineering
│    & Cleaning)      │  (month, quarter, is_weekend, revenue_per_unit)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  MySQL Database     │  Cleaned rows loaded per dataset into isolated
│  (database_loader)  │  tables; duplicate/invalid rows prevented
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  SQL Analytics      │  Aggregations, revenue summaries, product/customer
│  (sql_analysis.py)  │  rankings executed against the loaded tables
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  ML Pipeline        │  Feature matrix construction → train/test split
│  (ml/)              │  (80/20) → model training → serialized to .pkl
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Evaluation         │  MAE, RMSE, R², Adjusted R², MAPE, 5-fold CV,
│  (ml/evaluate.py)   │  overfitting assessment, feature importance,
│                     │  permutation importance, confidence intervals,
│                     │  residual plots, ROI analysis
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Frontend Export    │  JSON artifacts written to /frontend/public/
│  (frontend_export)  │  for static rendering in the Next.js dashboard
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Next.js Dashboard  │  KPI cards, revenue trend charts, product
│  (frontend/)        │  performance, segmentation, model metrics view
└─────────────────────┘
```

**Feature columns used for ML:**  
`month`, `quarter`, `day_of_week`, `is_weekend`, `quantity`, `price`, `category_encoded`, `customer_id`, `product_id`, `revenue_per_unit`

**Target column:** `revenue`

---

## 📊 Model Details

### Why Three Models?

The goal was not to pick one model and declare victory. Three architecturally different regressors were trained on the same features so that performance differences reflect real structural trade-offs rather than hyperparameter luck.

- **Linear Regression** serves as the interpretability baseline. If the non-linear models offer no lift, it signals the relationships are already linear.
- **Random Forest** handles non-linearity, feature interactions, and noisy data without requiring scaling. With 300 trees and controlled depth, it avoids both underfitting and heavy overfitting.
- **XGBoost** tests whether sequential gradient boosting outperforms the bagging approach of Random Forest on this data. It is configured conservatively with regularization to prevent overfitting on smaller subsets.

### Why Random Forest Outperformed XGBoost Here

On both datasets, Random Forest consistently achieved higher R² and lower error than XGBoost. The primary reason is the nature of the feature distribution: `price` and `quantity` together explain the overwhelming majority of revenue variance (~96–97% combined feature importance). In this scenario, the additive corrections that XGBoost applies offer marginal benefit, while Random Forest's ensemble averaging produces lower variance predictions out of the box. Random Forest also requires no feature scaling and is more forgiving of the ordinal encoded categorical columns used in this pipeline.

### Evaluation Metrics

| Metric | Description |
|---|---|
| **MAE** | Mean Absolute Error — average dollar error per prediction |
| **RMSE** | Root Mean Squared Error — penalizes large individual errors |
| **R²** | Proportion of revenue variance explained by the model |
| **Adjusted R²** | R² corrected for number of features |
| **MAPE** | Mean Absolute Percentage Error — error as % of actual revenue |
| **CV R²** | 5-fold cross-validated R² — measures generalization stability |

---

## 📈 Results & Performance

### Dataset 1 – Model Performance

**Dataset:** `Retail_Transactions_2024` — Global E-Commerce Sales | 1,810 samples | 80/20 train-test split

| Metric | ⭐ Random Forest | XGBoost | Linear Regression |
|---|---|---|---|
| **R²** | **0.9853** | 0.9841 | 0.6846 |
| **Adjusted R²** | **0.9849** | 0.9837 | 0.6766 |
| **MAE** | **$5.34** | $9.70 | $54.41 |
| **RMSE** | **$18.37** | $19.08 | $85.08 |
| **MAPE** | **2.50%** | 8.40% | 74.44% |
| **CV Mean R²** | **0.9911** | N/A¹ | N/A¹ |
| **CV Std R²** | **0.0061** | N/A¹ | N/A¹ |
| **Fit Assessment** | Good fit | Good fit | Good fit |

> ¹ 5-fold cross-validation was performed on the best model only (Random Forest). CV Mean R² = **0.9911**, CV Std R² = **0.0061** — confirming strong generalization with minimal variance across folds.

**Key Insights — Dataset 1:**
- `price` (63.04%) and `quantity` (36.56%) account for ~99.6% of all feature importance
- Best revenue month: **October**; lowest revenue month: **January**
- Weekend average revenue ($166.64) exceeds weekday average ($155.13)
- Top product by revenue: **Mesh Back Task Chair** ($16,320.85)

---

### Dataset 2 – Model Performance

**Dataset:** `Market_Trend_Data_2025` — Retail Supply Chain Sales | 8,820 samples | 80/20 train-test split

| Metric | ⭐ Random Forest | XGBoost | Linear Regression |
|---|---|---|---|
| **R²** | **0.9384** | 0.9374 | 0.7142 |
| **Adjusted R²** | **0.9381** | 0.9371 | 0.7128 |
| **MAE** | **$13.94** | $14.70 | $36.89 |
| **RMSE** | **$28.71** | $28.95 | $61.85 |
| **MAPE** | **25.47%** | 30.20% | 103.52% |
| **CV Mean R²** | **0.9352** | N/A¹ | N/A¹ |
| **CV Std R²** | **0.0109** | N/A¹ | N/A¹ |
| **Fit Assessment** | Good fit | Good fit | Good fit |

> ¹ 5-fold cross-validation was performed on the best model only (Random Forest). CV Mean R² = **0.9352**, CV Std R² = **0.0109** — strong predictive performance maintained across all 5 folds (min fold R² = 0.924).

**Key Insights — Dataset 2:**
- `price` correlation with revenue: **0.784** (strongest driver)
- Best revenue month: **November**; lowest revenue month: **February**
- Price-revenue correlation is roughly 5× stronger than quantity-revenue correlation

---

## 💰 ROI & Business Impact

The pipeline includes an automated ROI analysis that models the financial benefit of using ML predictions to reduce inventory mismatches.

### How It Works

1. **Overstock savings**: When the model predicts higher than actual demand, the delta is multiplied by a 10% carrying cost reduction rate.
2. **Understock savings**: When the model predicts lower than actual demand, the delta is multiplied by a 15% lost-revenue recovery rate.
3. **Annual savings** are projected by scaling from the test set to the full dataset size.
4. **Implementation cost** is conservatively estimated at 20% of projected annual savings.
5. **ROI%** = `(Annual Savings − Implementation Cost) / Implementation Cost × 100`

### Results

| Dataset | Annual Savings | Implementation Cost | ROI |
|---|---|---|---|
| `Retail_Transactions_2024` | $1,328.57 | $265.71 | **400%** |
| `Market_Trend_Data_2025` | $15,493.05 | $3,098.61 | **400%** |

These figures are calculated entirely from model prediction error on the held-out test set, not from assumed market benchmarks.

---

## 🚀 How to Run the Project

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm / pnpm
- MySQL server running locally (for the database stage)
- A `.env` file with your MySQL credentials (see `.env.example` if present)

---

### 1. Clone the Repository

```bash
git clone https://github.com/adityagangwani30/sales-sense-ai.git
cd sales-sense-ai
```

---

### 2. Backend Setup (Python)

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

Configure your `.env` file:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=sales_sense
```

---

### 3. Run the Full Data Pipeline

Runs preprocessing → database load → SQL analytics → visualizations → frontend export for one dataset:

```bash
# Run for Dataset 1 (Retail_Transactions_2024)
python pipeline.py --dataset dataset_1

# Run for Dataset 2 (Market_Trend_Data_2025)
python pipeline.py --dataset dataset_2

# Run both datasets sequentially
python pipeline.py --dataset all
```

---

### 4. Run the ML Training & Evaluation Pipeline

```bash
# Train models and evaluate — Dataset 1
python main.py --dataset dataset_1

# Train models and evaluate — Dataset 2
python main.py --dataset dataset_2
```

This runs: preprocessing → feature engineering → model training → evaluation → business insights → report generation.

To run only the evaluation stage on already-trained models:

```bash
python ml/main.py --dataset dataset_1 --mode evaluate
```

---

### 5. Frontend Dashboard

```bash
cd frontend
npm install       # or: pnpm install
npm run dev       # or: pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The dashboard reads from static JSON files exported by `frontend_export.py`. Run the full pipeline at least once to populate the data before starting the frontend.

---

## 📁 Project Structure

```
sales-sense-ai/
│
├── original_dataset/               # Raw input files (not committed)
│   ├── global_ecommerce_sales.csv
│   └── Retail-Supply-Chain-Sales-Dataset.xlsx
│
├── data/
│   ├── raw/                        # Staging area for raw data
│   └── processed/                  # Cleaned output staging
│
├── ml/                             # ML pipeline module
│   ├── data_loader.py              # Loads cleaned datasets for ML
│   ├── models.py                   # Model definitions (RF, XGBoost, LR)
│   ├── preprocessing.py            # Feature matrix construction
│   ├── train_test_split.py         # 80/20 stratified split
│   ├── evaluate.py                 # Full evaluation engine
│   └── main.py                     # ML pipeline entry point
│
├── src/                            # Orchestration wrappers
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   ├── evaluation.py
│   └── insights.py
│
├── frontend/                       # Next.js dashboard
│   ├── app/                        # App Router pages
│   ├── components/                 # Chart and UI components
│   │   ├── dashboard-deep-analytics.tsx
│   │   ├── revenue-trend-chart.tsx
│   │   ├── customer-segmentation-panel.tsx
│   │   ├── top-products-chart.tsx
│   │   ├── kpi-card.tsx
│   │   └── ...
│   ├── public/                     # Static JSON assets (pipeline output)
│   └── package.json
│
├── outputs/                        # All pipeline outputs (auto-generated)
│   ├── dataset_1/                  # Reports, plots, cleaned data
│   ├── dataset_2/
│   └── ml/
│       ├── dataset_1/              # Model artifacts + evaluation results
│       │   ├── random_forest.pkl
│       │   ├── xgboost.pkl
│       │   ├── metrics_detailed.json
│       │   ├── cross_validation.json
│       │   ├── feature_importance.json
│       │   ├── roi_analysis.json
│       │   ├── final_report.txt
│       │   └── plots/
│       └── dataset_2/
│
├── models/                         # Alternative model artifact storage
├── config/                         # Configuration files
├── docs/                           # Documentation assets
│
├── pipeline.py                     # Main data pipeline runner
├── main.py                         # ML training + evaluation runner
├── database_loader.py              # MySQL load logic
├── sql_analysis.py                 # SQL query execution layer
├── visualization.py                # Matplotlib/Seaborn plot generation
├── frontend_export.py              # JSON export for dashboard
├── convert_outputs.py              # Output format conversion utility
├── requirements.txt
└── README.md
```

---

## 🧪 Future Improvements

- **Hyperparameter tuning** — Add Optuna or GridSearchCV for automated Random Forest and XGBoost tuning
- **Real-time data integration** — Replace static JSON exports with a FastAPI backend serving live model predictions
- **Deployment** — Containerize the Python pipeline with Docker; deploy the Next.js dashboard to Vercel
- **Advanced models** — Evaluate LightGBM, CatBoost, and stacking ensembles for further accuracy gains
- **Time-series forecasting** — Extend to Prophet or LSTM for multi-step ahead revenue forecasting
- **Automated retraining** — Trigger model retraining via CI/CD when new data arrives
- **Alerting** — Add threshold-based anomaly detection and email/Slack alerts for revenue drops

---

## 👨‍💻 Author

**Aditya Gangwani**  
B.E Student | Data Science & AI Enthusiast

Building systems that bridge the gap between raw data and real decisions. SalesSense AI was designed to demonstrate a complete, production-style analytics pipeline — not just isolated notebook experiments.

- GitHub: [@adityagangwani30](https://github.com/adityagangwani30)

---
