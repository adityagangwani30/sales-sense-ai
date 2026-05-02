# Results Analysis

SalesSense AI converts model output into business-facing insights that can be read directly in the dashboard and generated reports.

## Model Comparison Summary

The platform compares Linear Regression, Random Forest, and XGBoost on the same feature set.

- Linear Regression provides a simple baseline.
- Random Forest usually gives the strongest balance of accuracy and stability in the exported runs.
- XGBoost offers an additional boosted-tree benchmark for more advanced nonlinear fit.

The project keeps the comparison transparent by exporting the same metric set for every model.

## Feature Importance Insights

The feature importance exports typically highlight a small set of drivers that matter most for prediction.

- quantity
- price
- customer and product identifiers
- category encoding
- time-based features such as month and day of week

These signals suggest that both commercial value and calendar timing influence revenue patterns.

## Error Analysis

The error analysis section focuses on how predictions deviate from actual values.

- residual distributions help reveal bias and spread
- percentile bands show where the largest errors occur
- confidence scores indicate how reliable predicted intervals are
- worst prediction samples help identify specific cases that deserve attention

This is useful for determining whether a model is genuinely reliable or merely fit to average behavior.

## Business Insights Overview

The pipeline also generates narrative insights for retail decision-makers.

- peak and weak revenue periods
- top products by revenue
- category performance contributions
- customer segmentation patterns
- ROI-based improvement opportunities

The ROI output is especially important because it frames model value in operational terms, such as savings, cost, and expected return.

## Practical Reading of the Results

For a portfolio review, the key message is that SalesSense AI is not just training models. It is producing a complete decision-support flow from raw retail data to interpretable business output.