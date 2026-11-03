# Interactive dashboard

Streamlit dashboard for revenue, product and country performance, customer behaviour, RFM segments, cohort retention, data quality, and inactivity model evaluation.

## Run locally

1. Download the latest ecommerce-customer-intelligence-outputs artifact from the [Build analytics outputs workflow](https://github.com/Karanaldo-07/ecommerce-customer-intelligence/actions/workflows/analytics.yml).
2. Extract the archive into the repository root, preserving data/processed and reports folders.
3. Install dependencies with: pip install -r requirements.txt
4. Start the app with: streamlit run app.py

The app reads precomputed CSV and JSON outputs. It does not rerun model training on each page load.

## Deployment

For Streamlit Community Cloud, deploy this repository with app.py as the entry point. The generated aggregate dashboard CSVs and JSON reports must be present in the deployed repository or supplied through an external data store. Do not publish the raw customer-level transaction workbook or model artifacts unnecessarily.
