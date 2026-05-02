# Data Dictionary

This dictionary describes the most important fields used across the pipeline, SQL outputs, ML features, and dashboard summaries. Some source columns vary slightly by dataset, so aliases are listed where needed.

## Core Dataset Fields

| Column | Meaning | Type |
| --- | --- | --- |
| `date` / `order_date` | Transaction date used for time-based analysis and monthly aggregation | date |
| `year` | Calendar year when present in the source | int |
| `month` | Month number or month label used in time features | int / string |
| `quarter` | Calendar quarter derived from the date | int |
| `day_of_week` | Day index derived from the transaction date | int |
| `is_weekend` | Weekend flag derived from the transaction date | bool / int |
| `sales` / `revenue` | Primary target and revenue value used in the pipeline | float |
| `quantity` | Units sold for a transaction or line item | int / float |
| `price` | Unit price or sale price used for feature engineering | float |
| `customer_id` | Customer identifier used for segmentation and modeling | int / string |
| `customer` / `customer_name` | Customer label when the source uses names instead of numeric IDs | string |
| `product_id` | Product identifier used for modeling and product analysis | int / string |
| `product` / `product_name` | Product label used in dashboards and SQL summaries | string |
| `category` / `product_category` / `sub_category` | Product grouping used for category analysis | string |
| `segment` / `customer_segment` | Customer grouping used for segmentation analysis | string |

## Engineered ML Features

| Column | Meaning | Type |
| --- | --- | --- |
| `month` | Derived numeric month feature used by the ML models | int |
| `quarter` | Derived quarter feature used by the ML models | int |
| `day_of_week` | Derived weekday feature used by the ML models | int |
| `is_weekend` | Derived binary feature for weekend behavior | int |
| `category_encoded` | Encoded category label for model input | int |
| `customer_id` | Encoded customer identifier for model input | int |
| `product_id` | Encoded product identifier for model input | int |

## Dashboard KPI Fields

| Column | Meaning | Type |
| --- | --- | --- |
| `total_revenue` | Total revenue analyzed for a dataset | float |
| `total_orders` | Total order count analyzed for a dataset | int |
| `total_customers` | Number of unique customers analyzed | int |
| `avg_order_value` | Average order value | float |
| `repeat_purchase_rate` | Percentage of customers with more than one order | float |
| `trend_change_pct` | Percentage change in revenue between the last two monthly periods | float |

## ML and Evaluation Outputs

| Column | Meaning | Type |
| --- | --- | --- |
| `sample_count` | Number of model rows used in training/evaluation outputs | int |
| `mae` | Mean absolute error | float |
| `mse` | Mean squared error | float |
| `rmse` | Root mean squared error | float |
| `r2` | Coefficient of determination | float |
| `adjusted_r2` | Adjusted R-squared | float |
| `mape` | Mean absolute percentage error | float |
| `train_r2` | Training R-squared | float |
| `test_r2` | Test R-squared | float |
| `generalization_gap` | Difference between train and test R-squared | float |
| `fit_assessment` | Qualitative fit label such as good fit or overfitting | string |

## ROI Output Fields

| Column | Meaning | Type |
| --- | --- | --- |
| `savings` / `annual_savings` | Estimated savings from the ROI analysis | float |
| `cost` / `implementation_cost` | Estimated implementation cost | float |
| `roi` / `roi_pct` | Return on investment percentage | float |
| `text` | Human-readable ROI report text | string |

## Notes

- The frontend supports both snake_case and camelCase keys for compatibility.
- Some fields are generated only in exports and not stored in the raw source data.