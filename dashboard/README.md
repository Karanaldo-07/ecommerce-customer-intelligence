# Interactive dashboard

Streamlit dashboard for revenue, product and country performance, customer behaviour, RFM segments, cohort retention, data quality, and inactivity model evaluation.

## Data and privacy

The dashboard reads the aggregate-only files in `dashboard_data/`. The analytics workflow creates these from the full processed outputs and commits only aggregate tables and summary JSON. Customer IDs, invoice IDs, individual customer feature rows, raw transactions, and trained model binaries are not included in the public dashboard data folder.

## Run locally

1. Open the [Build analytics outputs workflow](https://github.com/Karanaldo-07/ecommerce-customer-intelligence/actions/workflows/analytics.yml) and click **Run workflow**.
2. Wait for the run to complete. It downloads the official UCI workbook, runs the analysis, creates aggregate dashboard tables, and commits refreshed files to `dashboard_data/`.
3. Clone or pull the repository.
4. Install dependencies with `pip install -r requirements.txt`.
5. Start the app with `streamlit run app.py`.

The app reads precomputed aggregate CSV and JSON outputs. It does not retrain models on page load.

## Publish with Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud with GitHub.
2. Choose **New app**, select this repository and the `main` branch.
3. Set the main file path to `app.py`.
4. Deploy. The root `requirements.txt` contains the dashboard dependencies.

After refreshing the analysis, the workflow commits updated aggregate tables to `main`; the deployed app can pick up the repository update through its normal redeploy/reboot flow.
