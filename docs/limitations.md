# Limitations

SalesSense AI is designed as a portfolio-ready analytics platform, but it has a few important limitations.

## Static Data Limitation

The frontend reads exported JSON and text artifacts from the public directory. That means the dashboard does not fetch fresh data on demand.

## No Real-Time Backend

There is currently no live API layer serving dashboard requests.

- the data is prepared ahead of time
- the frontend uses static snapshots
- changes require re-running the export pipeline

## Limited Dataset Scope

The repository currently focuses on two isolated datasets.

- `dataset_1`
- `dataset_2`

This keeps the project clean and reproducible, but it limits the breadth of benchmarking and comparison.

## Additional Constraints

- Model performance depends on the quality and shape of the input dataset.
- Business insights are derived from exported artifacts, not live operational events.
- Some visualizations and metrics are available only after the pipeline and export steps are run.