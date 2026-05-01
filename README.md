# SalesSense AI

SalesSense AI is a retail analytics and sales intelligence platform that turns two separate retail datasets into cleaned data, database-backed analytics, machine learning evaluation, and demo-ready dashboard assets.

## 1. Project Title & Tagline

**SalesSense AI** is a dataset-isolated retail intelligence system for preprocessing, SQL analytics, machine learning evaluation, and business insight generation.

## 2. Overview

SalesSense AI was built to demonstrate an end-to-end analytics workflow for retail decision support. It takes raw sales data, standardizes and enriches it, loads it into MySQL, runs SQL-based business analysis, trains and evaluates regression models, and exports structured artifacts for a Next.js dashboard.

The project solves a common real-world problem: retail data is usually fragmented across files, database tables, and reporting layers. SalesSense AI consolidates that workflow into one reproducible pipeline so analysts can compare datasets, validate model quality, and generate business-facing insights without mixing sources.

The implementation currently supports two fully isolated datasets:

- `dataset_1` - Global E-Commerce Sales
- `dataset_2` - Retail Supply Chain Sales

Each dataset is processed independently from ingestion through final reporting.

## 3. Features

- Data preprocessing pipeline that cleans raw CSV / Excel inputs, standardizes columns, handles missing values, removes invalid rows, and engineers time-based and business features.
- SQL analytics backed by MySQL integration for structured relational analysis.
- ML-based prediction using Linear Regression, Random Forest, and XGBoost.
- Model comparison with evaluation metrics, cross-validation, overfitting checks, and error analysis.
- Business insights generation for revenue drivers, seasonal trends, product performance, customer behavior, and ROI estimation.
- Interactive dashboard support through Next.js with static JSON-based data assets for demo usage.
- Multi-dataset support with strict dataset isolation between `dataset_1` and `dataset_2`.

## 4. Architecture

```text
Dataset → Pipeline → Database → ML → Insights → Dashboard
```

The runtime flow is:

1. Load one dataset at a time.
2. Clean and engineer the data.
3. Store the processed data in MySQL.
4. Train or reuse saved ML models.
5. Evaluate the models and generate business insights.
6. Export JSON, CSV, and report assets for the dashboard.

This design keeps the analytics stack modular while preserving strict dataset isolation.

## 5. Tech Stack

- Python: `pandas`, `numpy`, `scikit-learn`, `xgboost`, `scipy`
- Data visualization: `matplotlib`, `seaborn`
- Database: MySQL with `mysql-connector-python`
- Frontend: Next.js, Tailwind CSS
- File formats: CSV, JSON, PKL
- Supporting utilities: `python-dotenv`, `openpyxl`, `PyYAML`

## 6. Project Structure

```text
sales-sense-ai/
	data/
		raw/
		processed/
	ml/
	pipeline/
	frontend/
	outputs/
		dataset_1/
		dataset_2/
	models/
		dataset_1/
		dataset_2/
	docs/
	config/
	main.py
	requirements.txt
	README.md
```

Additional implementation folders used by the project include `src/` for orchestration wrappers and `original_dataset/` for the source inputs.

## 7. How to Run

### Backend / ML:

```bash
pip install -r requirements.txt
python main.py --dataset dataset_1
```

To run the ML evaluation stage directly on an existing trained model set:

```bash
python ml/main.py --dataset dataset_1 --mode evaluate
```

### Frontend:

```bash
cd frontend
npm install
npm run dev
```

Recommended dataset values:

- `dataset_1`
- `dataset_2`

## 8. Dataset Information

SalesSense AI currently uses two datasets with different retail contexts:

- `dataset_1` is sourced from `original_dataset/global_ecommerce_sales.csv`
- `dataset_2` is sourced from `original_dataset/Retail-Supply-Chain-Sales-Dataset.xlsx`

Dataset isolation is enforced throughout the pipeline. Each dataset has its own cleaned output, model artifacts, plots, reports, and dashboard exports. No files are merged across datasets, and every evaluation run is scoped to one dataset identifier.

## 9. Machine Learning Details

The ML layer uses three regression models:

- Linear Regression
- Random Forest
- XGBoost

Evaluation and comparison include:

- MAE
- MSE
- RMSE
- R²
- Adjusted R²
- MAPE
- 5-fold cross-validation
- overfitting checks
- error analysis and residual diagnostics
- feature importance and permutation importance

Model selection is based on the best test performance, with supporting checks from cross-validation and fit-quality comparison. In the current implementation, Random Forest is typically selected as the best model for the final report for both datasets because it provides the strongest and most stable balance of accuracy and interpretability in the evaluated runs.

## 10. Results & Insights

The pipeline generates reporting artifacts that translate model output into business language. For the current evaluated runs, the final reports show strong predictive performance and produce actionable findings such as:

- dominant revenue drivers such as price and quantity
- best and worst months by revenue
- top and bottom products by revenue contribution
- weekend versus weekday patterns
- ROI estimates based on overstock and understock reduction assumptions

Example outputs are written into dataset-specific folders such as:

- `outputs/dataset_1/reports/final_report.txt`
- `outputs/dataset_2/reports/final_report.txt`

The ML evaluation stage also writes detailed artifacts including metrics, confidence scores, worst predictions, and feature importance comparisons.

## 11. Screenshots (Placeholder Section)

```markdown
![Dashboard](path/to/image.png)
```

## 12. Future Improvements

- Real-time backend integration for live analytics and model refreshes
- Additional datasets and broader retail use cases
- Advanced models such as tuned gradient boosting or ensemble stacking
- Automated alerting for anomalies and forecasting drift
- Deeper frontend integration for live report rendering

## 13. License

This project is licensed under the MIT License.

## 14. Author

- Name: Your Name
- GitHub: https://github.com/your-username
