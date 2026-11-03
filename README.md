# E-Commerce Customer Intelligence & Revenue Analytics

An end-to-end, portfolio-grade data science project exploring e-commerce transactions, customer behaviour, revenue performance, segmentation, and churn risk.

> **Project status:** Dataset selected and project foundation created. Analysis, models, metrics, and dashboard results will be added only after they have been implemented and validated. No performance claims are made at this stage.

## Business problem

An online retailer wants to understand what drives revenue, which customers are most valuable, how purchasing behaviour changes over time, and which customers may be at risk of becoming inactive. This project will turn transactional data into reproducible analysis and decision-support outputs.

## Dataset

We selected **UCI Online Retail II**: 1,067,371 transaction line-items covering 1 December 2009 to 9 December 2011. It contains invoice, product, quantity, timestamp, unit price, customer ID, and country fields. The source includes missing customer IDs and cancellation/return records, which will be profiled and handled transparently.

- [Official UCI dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- DOI: https://doi.org/10.24432/C5CG6D
- License: CC BY 4.0
- Creator: Daqing Chen

See [data/README.md](data/README.md) for download instructions, field definitions, handling principles, and attribution.

## Planned deliverables

1. **Data ingestion and data quality** — reproducible download, schema inspection, missingness, duplicates, cancellations, returns, and validation checks.
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
│   ├── raw/                 # Original data; excluded from Git
│   └── README.md            # Dataset source, data dictionary, handling
├── notebooks/               # Ordered analysis notebooks
├── scripts/                 # Reproducible data acquisition scripts
├── sql/
│   └── schema.sql
├── src/
│   └── ecommerce_intel/
├── reports/
│   └── figures/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Getting started

1. Use Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Download the dataset: `python scripts/download_data.py`.
5. Read [data/README.md](data/README.md) before analysis.
6. Configure local database credentials using `.env.example`. Never commit real credentials.

## Evaluation principles

- Split data by time when the prediction task is time-dependent.
- Prevent target leakage during feature engineering.
- Compare against simple baselines.
- Report class balance and threshold-dependent metrics.
- Explain limitations and avoid presenting correlation as causation.
- Record random seeds, package versions, and experiment settings.

## Current status

- [x] Repository foundation and project scope
- [x] Select and document a public dataset
- [x] Initial ingestion, cleaning, analytics, and RFM segmentation modules
- [x] Unit tests and GitHub Actions CI workflow added
- [ ] Execute CI and resolve any failures
- [ ] Download and validate the full raw workbook
- [ ] Full dataset SQL analysis and EDA
- [ ] Time-based inactivity target and validated churn model
- [ ] Dashboard, business recommendations, and deployment

## Run the project

Install dependencies with `pip install -r requirements.txt`, download the source workbook using `python scripts/download_data.py`, then run `python scripts/run_analysis.py`. The pipeline writes generated files under `data/processed/` and a quality report under `reports/`. Run tests with `pytest -q`.

The current model module deliberately refuses to train unless a chronological observation window and future inactivity label are supplied. This prevents a misleading churn result from being manufactured from a single undivided transaction history.

## Author

Karan Bhise — B.E. Artificial Intelligence & Data Science.

This is an independent portfolio project, not professional client work.
