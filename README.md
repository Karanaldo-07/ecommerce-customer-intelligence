# E-Commerce Customer Intelligence & Revenue Analytics

An end-to-end, portfolio-grade data science project exploring e-commerce transactions, customer behaviour, revenue performance, segmentation, and churn risk.

> **Project status:** Full-dataset EDA and baseline inactivity modelling have been executed successfully. Power BI dashboard specifications and DAX measures are available under `powerbi/`. The model is a research baseline, not a production churn system.

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
2. **SQL analytics** — revenue trends, product performance, repeat purchase behaviour, cohort retention, country contribution, and cancellation monitoring. See `sql/business_analysis.sql`.
3. **Exploratory analysis** — automated monthly revenue, country and product performance, order-value distribution, customer repeat-purchase summary, and cohort-retention visualizations. EDA tables are written to `data/processed/eda_*.csv`; charts and `reports/eda_summary.json` are written under `reports/`.
4. **Customer segmentation** — RFM features (recency, frequency, monetary value), baseline segments, and interpretation.
5. **Churn / inactivity modelling** — create monthly customer snapshots from a 180-day lookback, label inactivity in the following 90 days, and compare Logistic Regression with Random Forest using a chronological holdout and precision, recall, F1, ROC-AUC and PR-AUC.
6. **Business recommendations** — validated findings and testable retention/merchandising actions are documented in `reports/business_findings.md`.
7. **Dashboard** — interactive Streamlit dashboard in `app.py`; Power BI import guide and DAX measures are available in `powerbi/`.

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
3. Install full project dependencies: `pip install -r requirements-dev.txt`.
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
- [x] Advanced SQL business-analysis query pack
- [x] Monthly customer cohort-retention analysis with automated tests
- [x] Reproducible EDA tables, summary metrics, and charts integrated into the pipeline
- [x] Leakage-aware monthly inactivity snapshot builder and baseline model comparison implemented
- [x] Unit tests and GitHub Actions CI workflow added
- [x] Execute CI and resolve initial failures
- [x] Download and validate the full raw workbook
- [ ] Execute SQL pack against PostgreSQL and interpret business findings
- [x] Generate full-dataset exploratory analysis tables and charts
- [x] Interpret full-dataset EDA findings and document business recommendations
- [x] Validate inactivity model training and metrics on the complete dataset
- [x] Prepare Power BI data model guide and DAX measures
- [x] Build interactive Streamlit dashboard with revenue, country, product, customer, cohort, model, and data-quality views
- [x] Publish privacy-safe aggregate dashboard datasets\n- [x] Add automated dashboard data-contract and privacy validation\n- [x] Add interactive business recommendations and scenario planning

## Run the project

Install full project dependencies with `pip install -r requirements-dev.txt`, download the source workbook using `python scripts/download_data.py`, then run `python scripts/run_analysis.py`. The pipeline writes processed tables under `data/processed/`, quality and EDA summaries under `reports/`, and charts under `reports/figures/`. Run tests with `pytest -q`.

The current model module deliberately refuses to train unless a chronological observation window and future inactivity label are supplied. This prevents a misleading churn result from being manufactured from a single undivided transaction history.

## Author

Karan Bhise — B.E. Artificial Intelligence & Data Science.

This is an independent portfolio project, not professional client work.


## Validated full-dataset snapshot (3 November 2026)

- 1,067,371 raw transaction rows; 1,041,670 valid sale lines.
- £20.97M valid-sale revenue across 40,077 invoices; average invoice value £523.31.
- 5,878 identified customers; 72.39% are repeat customers among identified customers.
- Logistic Regression baseline: inactive-class precision 58.6%, recall 79.5%, F1 0.675, ROC-AUC 0.728, PR-AUC 0.640 on a chronological holdout.
- Random Forest baseline: inactive-class precision 59.1%, recall 74.8%, F1 0.661, ROC-AUC 0.715, PR-AUC 0.624 on the same holdout.

See [reports/business_findings.md](reports/business_findings.md) for definitions, caveats, and recommendations. The inactivity label means no purchase in the next 90 days; it is not a definitive prediction of permanent churn. See [powerbi/README.md](powerbi/README.md) and [powerbi/measures.dax](powerbi/measures.dax) for the dashboard build guide.


## Interactive dashboard

Run `streamlit run app.py` after downloading and extracting the latest analytics artifact into the repository root. Setup instructions are in [dashboard/README.md](dashboard/README.md). The app uses the generated aggregate CSV/JSON outputs and does not retrain the models when it starts.
