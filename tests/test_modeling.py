import pandas as pd
import pytest
from ecommerce_intel.modeling import build_inactivity_dataset, train_inactivity_baseline


def synthetic_transactions():
    rows = []
    # Customers A/B/C/D have repeat purchases; E/F/G/H become inactive.
    for customer in ["A", "B", "C", "D", "E", "F", "G", "H"]:
        for month in range(1, 19):
            should_buy = month <= 8 or (customer in ["A", "B", "C", "D"] and month % 2 == 0)
            if should_buy:
                rows.append({
                    "customer_id": customer,
                    "invoice_no": f"{customer}-{month}",
                    "invoice_date": pd.Timestamp("2010-01-01") + pd.DateOffset(months=month-1),
                    "line_revenue": 20.0 + (ord(customer) - 64) * month,
                    "is_valid_sale": True,
                })
    return pd.DataFrame(rows)


def test_inactivity_dataset_uses_future_window_labels():
    data = build_inactivity_dataset(synthetic_transactions(), lookback_days=90, horizon_days=60)
    assert not data.empty
    assert set(data["is_inactive"].unique()) == {0, 1}
    assert data["observation_end"].max() < synthetic_transactions()["invoice_date"].max()
    assert (data[["recency_days", "frequency_180d", "monetary_180d"]] >= 0).all().all()


def test_model_requires_both_future_label_classes():
    frame = pd.DataFrame({
        "recency_days": [1, 2], "frequency_180d": [2, 1],
        "monetary_180d": [30, 10], "is_inactive": [1, 1],
        "observation_end": pd.to_datetime(["2011-01-31", "2011-02-28"])
    })
    with pytest.raises(ValueError, match="both classes"):
        train_inactivity_baseline(frame)
