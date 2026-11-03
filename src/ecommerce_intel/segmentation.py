"""Rule-based RFM segmentation with deterministic, explainable labels."""
import pandas as pd

def segment_customers(rfm: pd.DataFrame) -> pd.DataFrame:
    required = {"customer_id","recency_days","frequency","monetary"}
    missing = required - set(rfm.columns)
    if missing:
        raise ValueError(f"RFM data missing columns: {sorted(missing)}")
    out = rfm.copy()
    if out.empty:
        out["segment"] = pd.Series(dtype="object")
        return out
    # Quantile ranks handle ties and small samples more safely than qcut.
    r = out["recency_days"].rank(method="average", pct=True, ascending=False)
    f = out["frequency"].rank(method="average", pct=True)
    m = out["monetary"].rank(method="average", pct=True)
    out["segment"] = "Needs Attention"
    out.loc[(r >= .75) & (f >= .75) & (m >= .75), "segment"] = "Champions"
    out.loc[(r >= .50) & (f >= .50), "segment"] = "Loyal Customers"
    out.loc[(r < .25) & (f >= .50), "segment"] = "At Risk"
    out.loc[(r >= .75) & (f < .25), "segment"] = "New Customers"
    return out
