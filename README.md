# E-Commerce Customer Intelligence & Revenue Analytics

An end-to-end, portfolio-grade data science project exploring e-commerce transactions, customer behaviour, revenue performance, segmentation, and churn risk.

> **Project status:** Foundation and project plan. Analysis, models, metrics, and dashboard results will be added only after they have been implemented and validated. No performance claims are made at this stage.

## Business problem

An online retailer wants to understand what drives revenue, which customers are most valuable, how purchasing behaviour changes over time, and which customers may be at risk of becoming inactive. This project will turn transactional data into reproducible analysis and decision-support outputs.

## Planned deliverables

1. **Data ingestion and data quality** — document the dataset source, schema, assumptions, missing values, duplicates, and validation checks.
2. **SQL analytics** — revenue trends, order patterns, repeat purchase behaviour, cohort retention, and customer-level metrics.
3. **Exploratory analysis** — customer, product, geography, and time-based analysis with clear visualizations.
4. **Customer segmentation** — RFM features (recency, frequency, monetary value), baseline segments, and interpretation.
5. **Churn / inactivity modelling** — define a leakage-safe target, build a baseline model, compare suitable models, and evaluate with precision, recall, F1, ROC-AUC and PR-AUC as appropriate.
6. **Business recommendations** — translate findings into testable retention and merchandising actions.
7. **Dashboard and API** — publish an interactive analytics dashboard and, if useful, a small prediction API.

## Initial technology stack

- Python, Pandas, NumPy
- PostgreSQL and SQL
- Matplotlib / Seaborn
- scikit-learn (and XGBoost only if justified)
- Power BI for the business dashboard
- FastAPI for optional model serving
- Git and GitHub

## Repository layout

```text
.
├── data/
│   ├── raw/                 # Original data; do not commit private/large data
│   ├── processed/           # Reproducible transformed data
│   └── README.md            # Dataset acquisition and data dictionary
├── notebooks/               # Ordered analysis notebooks
├── sql/
│   └── schema.sql           # Initial relational schema
├── src/
│   └── ecommerce_intel/     # Reusable project code
├── reports/
│   └── figures/             # Exported charts and report assets
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Getting started

1. Use Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Read [data/README.md](data/README.md) before downloading a dataset.
5. Configure local database credentials using `.env.example`. Never commit real credentials.
6. Work through notebooks in numerical order as they are added.

## Data and reproducibility

The dataset has not yet been selected. We will choose a public dataset with transaction-level records and document its license, source URL, columns, date coverage, and limitations before analysis. Raw datasets and personally identifiable information must not be committed to this repository.

## Evaluation principles

- Split data by time when the prediction task is time-dependent.
- Prevent target leakage during feature engineering.
- Compare against simple baselines.
- Report class balance and threshold-dependent metrics.
- Explain limitations and avoid presenting correlation as causation.
- Record random seeds, package versions, and experiment settings.

## Current status

- [x] Repository foundation and project scope
- [x] Initial relational schema
- [ ] Select and document dataset
- [ ] Data quality and SQL analysis
- [ ] EDA and statistical investigation
- [ ] RFM segmentation
- [ ] Churn modelling and model interpretation
- [ ] Dashboard, tests, and deployment

## Author

Karan Bhise — B.E. Artificial Intelligence & Data Science.

This is an independent portfolio project, not professional client work.
