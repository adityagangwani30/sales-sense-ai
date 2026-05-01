# Week 9 Architecture

The Week 9 integration adds a compatibility-first orchestration layer instead of replacing the working Week 1-8 code.

## Execution Flow

1. `main.py` starts the full pipeline for one dataset.
2. `src/preprocessing.py` invokes the existing preprocessing pipeline.
3. `src/feature_engineering.py` reuses the existing feature engineering logic.
4. `src/model_training.py` reuses saved Week 7 model artifacts and only trains if a required model is missing.
5. `src/evaluation.py` runs the Week 8 evaluation pipeline.
6. `src/insights.py` mirrors reports, metrics, plots, and model artifacts into the cleaned Week 9 directory layout.

## Dataset Isolation

All stages operate on a single dataset identifier and write only to that dataset's output paths.
