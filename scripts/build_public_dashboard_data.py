"""Export privacy-conscious aggregate tables for the public dashboard."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed"
TARGET = ROOT / "dashboard_data"
REPORTS = ROOT / "reports"


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    customers = pd.read_csv(SOURCE / "eda_customer_summary.csv")
    customers.groupby("customer_type", as_index=False).agg(
        customers=("customer_type", "size"),
        lifetime_revenue_gbp=("lifetime_revenue", "sum"),
    ).to_csv(TARGET / "customer_type_summary.csv", index=False)

    bands = pd.cut(customers["lifetime_revenue"],
        [-0.001, 100, 500, 1000, 5000, 10000, float("inf")],
        labels=["£0–100", "£100–500", "£500–1k", "£1k–5k", "£5k–10k", "£10k+"])
    bands.value_counts(sort=False).rename_axis("revenue_band").rename("customers").reset_index().to_csv(
        TARGET / "customer_revenue_bands.csv", index=False)

    segments = pd.read_csv(SOURCE / "customer_segments.csv")
    segments.groupby("segment", as_index=False).agg(customers=("segment", "size")).to_csv(
        TARGET / "segment_counts.csv", index=False)

    snapshots = pd.read_csv(SOURCE / "inactivity_training_data.csv", parse_dates=["observation_end"])
    snapshots.groupby("observation_end", as_index=False).agg(
        inactive_share=("is_inactive", "mean"), snapshot_count=("is_inactive", "size")
    ).to_csv(TARGET / "inactivity_monthly_summary.csv", index=False)

    copies = {
        "monthly_revenue.csv": "eda_monthly_revenue.csv",
        "country_performance.csv": "eda_country_performance.csv",
        "product_performance.csv": "eda_product_performance.csv",
        "cohort_retention.csv": "eda_cohort_retention.csv",
    }
    for target, source in copies.items():
        frame = pd.read_csv(SOURCE / source)
        if "cohort_month" in frame:
            frame["cohort_month"] = pd.to_datetime(frame["cohort_month"]).dt.strftime("%Y-%m-%d")
            frame["activity_month"] = pd.to_datetime(frame["activity_month"]).dt.strftime("%Y-%m-%d")
        frame.to_csv(TARGET / target, index=False)

    for name in ("eda_summary.json", "data_quality.json", "model_evaluation.json"):
        (TARGET / name).write_text((REPORTS / name).read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    main()
