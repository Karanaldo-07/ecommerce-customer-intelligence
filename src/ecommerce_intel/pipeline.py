"""Command-line data preparation and reporting pipeline."""
from pathlib import Path
import json
import pandas as pd
from .data import load_retail_workbook, clean_transactions, validate_transactions
from .analytics import monthly_revenue, country_performance, build_rfm, cohort_retention
from .segmentation import segment_customers
from .eda import run_eda

ROOT = Path(__file__).resolve().parents[2]

def run_pipeline(workbook: str | Path | None = None) -> dict:
    workbook = Path(workbook) if workbook else ROOT / "data/raw/online_retail_II.xlsx"
    output = ROOT / "data/processed"
    reports = ROOT / "reports"
    figures = reports / "figures"
    output.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    raw = load_retail_workbook(workbook)
    clean = clean_transactions(raw)
    quality = validate_transactions(clean)
    clean.to_parquet(output / "transactions.parquet", index=False)
    monthly_revenue(clean).to_csv(output / "monthly_revenue.csv", index=False)
    country_performance(clean).to_csv(output / "country_performance.csv", index=False)
    cohort_retention(clean).to_csv(output / "cohort_retention.csv", index=False)
    eda_summary = run_eda(clean, output, reports)
    rfm = build_rfm(clean)
    segmented = segment_customers(rfm)
    rfm.to_csv(output / "customer_rfm.csv", index=False)
    segmented.to_csv(output / "customer_segments.csv", index=False)
    (reports / "data_quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    return {"data_quality": quality, "eda_summary": eda_summary}

if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2))
