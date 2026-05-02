# System Design

SalesSense AI uses a modular design that separates data preparation, relational analytics, machine learning, and presentation.

## Why MySQL Is Used

MySQL is the structured analytics layer because it is well suited for:

- relational sales data
- grouping and aggregation queries
- SQL business reporting
- repeatable analysis across datasets

The project uses MySQL to support analysis that is more naturally expressed in SQL than in flat files.

## Why the Frontend Is Static

The frontend is intentionally static and reads exported files from `frontend/public/data/`.

- It avoids a runtime dependency on a live backend API.
- It loads quickly during demos and portfolio reviews.
- It can be deployed as a frontend-only experience.
- It is easier to validate because each dataset snapshot is pre-generated.

This design is appropriate because the project emphasizes analytics outputs rather than user-authenticated transactions.

## Core Design Decisions

- Dataset-specific directories are used for every output type.
- The pipeline produces reproducible artifacts instead of on-demand computation.
- The dashboard consumes normalized JSON files rather than raw database queries.
- The ML workflow is built to compare multiple regressors on the same feature set.
- The export layer mirrors reports into a simple structure that the frontend can read reliably.

## Scalability Considerations

The current implementation is optimized for a small number of curated retail datasets, but the architecture can scale further.

- A backend API could be added later for dynamic queries.
- A task queue could regenerate artifacts asynchronously.
- Additional datasets can be added by extending the dataset configuration and output paths.
- Caching can reduce repeated file reads for the dashboard.
- A database-backed API could replace static JSON when real-time updates are needed.

## Tradeoff Summary

The current design favors clarity, reproducibility, and low operational overhead over real-time flexibility. That is a good fit for a portfolio-grade analytics platform.