"""Validate public dashboard aggregates and prevent accidental customer-level publication."""
from pathlib import Path
import json
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dashboard_data"

REQUIRED_COLUMNS = {
    "monthly_revenue.csv": {"month", "revenue", "orders", "units"},
    "country_performance.csv": {"country", "revenue", "orders", "customers"},
    "product_performance.csv": {"stock_code", "description", "units_sold", "revenue", "invoice_count"},
    "customer_type_summary.csv": {"customer_type", "customers", "lifetime_revenue_gbp"},
    "customer_revenue_bands.csv": {"revenue_band", "customers"},
    "segment_counts.csv": {"segment", "customers"},
    "inactivity_monthly_summary.csv": {"observation_end", "inactive_share", "snapshot_count"},
    "cohort_retention.csv": {"cohort_month", "activity_month", "cohort_index", "customers", "cohort_size", "retention_rate"},
}
FORBIDDEN_COLUMN_TOKENS = ("customer_id", "invoice_no", "invoice_id", "customer_email", "email", "phone", "address")


def validate_dashboard_data(data_dir: Path = DATA) -> list[str]:
    """Return validation errors; aggregate count columns are allowed."""
    errors = []
    frames = {}
    for filename, expected in REQUIRED_COLUMNS.items():
        path = data_dir / filename
        if not path.exists():
            errors.append(f"Missing required file: {filename}")
            continue
        frame = pd.read_csv(path)
        frames[filename] = frame
        missing = expected - set(frame.columns)
        if missing:
            errors.append(f"{filename} missing columns: {sorted(missing)}")
        forbidden = [col for col in frame.columns
                     if any(token in col.lower().replace(" ", "_") for token in FORBIDDEN_COLUMN_TOKENS)]
        if forbidden:
            errors.append(f"{filename} contains restricted identifier columns: {forbidden}")
        if frame.empty:
            errors.append(f"{filename} must not be empty")

    for filename in ("data_quality.json", "eda_summary.json", "model_evaluation.json"):
        path = data_dir / filename
        if not path.exists():
            errors.append(f"Missing required file: {filename}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            errors.append(f"{filename} is not valid JSON: {exc}")

    monthly = frames.get("monthly_revenue.csv")
    if monthly is not None and {"revenue", "orders"}.issubset(monthly.columns):
        if (monthly["revenue"] < 0).any() or (monthly["orders"] < 0).any():
            errors.append("Monthly revenue and order counts must be non-negative")

    customer_types = frames.get("customer_type_summary.csv")
    if customer_types is not None and {"customer_type", "customers"}.issubset(customer_types.columns):
        if (customer_types["customers"] < 0).any():
            errors.append("Customer counts must be non-negative")
        if set(customer_types["customer_type"]) != {"One-time", "Repeat"}:
            errors.append("Customer type summary must contain One-time and Repeat aggregates")

    cohort = frames.get("cohort_retention.csv")
    if cohort is not None and "retention_rate" in cohort:
        if not cohort["retention_rate"].between(0, 1).all():
            errors.append("Cohort retention rates must be between 0 and 1")

    return errors


if __name__ == "__main__":
    problems = validate_dashboard_data()
    if problems:
        print("\n".join(f"ERROR: {problem}" for problem in problems))
        sys.exit(1)
    print("Dashboard aggregate validation passed. Required files, schemas, privacy checks and metric ranges are valid.")
