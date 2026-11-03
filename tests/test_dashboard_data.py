import json
import pandas as pd

from scripts.validate_dashboard_data import validate_dashboard_data


def write_valid_dashboard_bundle(path):
    frames = {
        "monthly_revenue.csv": pd.DataFrame([{"month":"2011-01-01","revenue":100.0,"orders":2,"units":4}]),
        "country_performance.csv": pd.DataFrame([{"country":"UK","revenue":100.0,"orders":2,"customers":1}]),
        "product_performance.csv": pd.DataFrame([{"stock_code":"A1","description":"Item","units_sold":4,"revenue":100.0,"invoice_count":2}]),
        "customer_type_summary.csv": pd.DataFrame([
            {"customer_type":"One-time","customers":1,"lifetime_revenue_gbp":20.0},
            {"customer_type":"Repeat","customers":1,"lifetime_revenue_gbp":80.0},
        ]),
        "customer_revenue_bands.csv": pd.DataFrame([{"revenue_band":"£0–100","customers":2}]),
        "segment_counts.csv": pd.DataFrame([{"segment":"Loyal Customers","customers":2}]),
        "inactivity_monthly_summary.csv": pd.DataFrame([{"observation_end":"2011-01-31","inactive_share":0.4,"snapshot_count":10}]),
        "cohort_retention.csv": pd.DataFrame([{"cohort_month":"2011-01-01","activity_month":"2011-01-01","cohort_index":1,"customers":2,"cohort_size":2,"retention_rate":1.0}]),
    }
    for name, frame in frames.items():
        frame.to_csv(path / name, index=False)
    for name in ("data_quality.json", "eda_summary.json", "model_evaluation.json"):
        (path / name).write_text(json.dumps({"status":"ok"}), encoding="utf-8")


def test_dashboard_data_contract_passes_for_aggregate_bundle(tmp_path):
    write_valid_dashboard_bundle(tmp_path)
    assert validate_dashboard_data(tmp_path) == []


def test_dashboard_data_contract_rejects_customer_identifiers(tmp_path):
    write_valid_dashboard_bundle(tmp_path)
    frame = pd.read_csv(tmp_path / "customer_type_summary.csv")
    frame["customer_id"] = ["C1", "C2"]
    frame.to_csv(tmp_path / "customer_type_summary.csv", index=False)
    errors = validate_dashboard_data(tmp_path)
    assert any("restricted identifier columns" in error for error in errors)


def test_dashboard_data_contract_rejects_invalid_retention_rate(tmp_path):
    write_valid_dashboard_bundle(tmp_path)
    frame = pd.read_csv(tmp_path / "cohort_retention.csv")
    frame.loc[0, "retention_rate"] = 1.5
    frame.to_csv(tmp_path / "cohort_retention.csv", index=False)
    errors = validate_dashboard_data(tmp_path)
    assert any("between 0 and 1" in error for error in errors)
