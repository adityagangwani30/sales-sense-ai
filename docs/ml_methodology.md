# ML Methodology

SalesSense AI uses a supervised regression workflow to predict revenue and to evaluate which model best fits each dataset.

## Models Used

- Linear Regression
- Random Forest Regressor
- XGBoost Regressor

These models provide a baseline-to-ensemble comparison that is easy to explain and suitable for tabular retail data.

## Feature Engineering

The preprocessing layer transforms raw retail records into model-ready features.

- Date values are converted into month, quarter, day-of-week, and weekend indicators.
- Categorical values such as category, customer, and product are encoded numerically.
- Numeric columns are coerced to numeric type and filled with robust median-based defaults when needed.
- The final feature matrix uses a consistent feature set so the same model comparison can be repeated across datasets.

## Train-Test Split

The evaluation pipeline uses an 80/20 train-test split with `random_state = 42`.

- 80 percent of the data is used for training.
- 20 percent is held out for testing and metric reporting.
- The fixed random seed keeps runs reproducible.

## Evaluation Metrics

Model quality is measured using:

- MAE: average absolute prediction error
- MSE: squared error sensitivity
- RMSE: square-rooted error magnitude
- R-squared: variance explained by the model
- Adjusted R-squared: R-squared adjusted for feature count
- MAPE: percentage error interpretation
- Cross-validation scores for stability checks
- Generalization gap for overfitting detection

## Model Selection Logic

The results table is sorted by best test R-squared, with RMSE used as a tie-breaker. The top row becomes the best model in the exported report.

Current runs in the repository commonly favor Random Forest because it balances accuracy and stability well on the available retail datasets.

## Interpretation Artifacts

The ML pipeline also exports:

- feature importance
- permutation importance
- residual and error analysis
- confidence scores
- worst predictions
- ROI analysis text and structured ROI values

These outputs turn raw model performance into business-readable reporting.