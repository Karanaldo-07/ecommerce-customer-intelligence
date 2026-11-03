"""Leakage-aware baseline customer inactivity model."""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ["recency_days","frequency","monetary"]

def train_inactivity_baseline(customer_features: pd.DataFrame, test_size: float = .25, random_state: int = 42):
    """Train a baseline only when a precomputed, time-safe binary target is supplied.

    Target must be 1 for inactive in a future observation window and must not
    be derived from the same period as the features.
    """
    required = set(FEATURES + ["is_inactive"])
    missing = required - set(customer_features.columns)
    if missing:
        raise ValueError(f"Model input missing columns: {sorted(missing)}")
    data = customer_features.dropna(subset=["is_inactive"]).copy()
    if data["is_inactive"].nunique() != 2:
        raise ValueError("is_inactive must contain both classes (0 and 1)")
    # Chronological split is required: caller provides observation_end per row.
    if "observation_end" not in data.columns:
        raise ValueError("Provide observation_end for a chronological train/test split")
    data["observation_end"] = pd.to_datetime(data["observation_end"])
    dates = sorted(data["observation_end"].dropna().unique())
    if len(dates) < 2:
        raise ValueError("At least two distinct observation_end dates are required")
    cutoff_index = max(1, min(len(dates)-1, int(len(dates)*(1-test_size))))
    cutoff = dates[cutoff_index]
    train = data[data["observation_end"] < cutoff]
    test = data[data["observation_end"] >= cutoff]
    if train.empty or test.empty or train["is_inactive"].nunique() < 2:
        raise ValueError("Chronological split does not contain enough examples/classes")
    pipe = Pipeline([("imputer", SimpleImputer(strategy="median")),("scale", StandardScaler()),("model", LogisticRegression(max_iter=1000, class_weight="balanced"))])
    pipe.fit(train[FEATURES], train["is_inactive"].astype(int))
    pred = pipe.predict(test[FEATURES])
    probability = pipe.predict_proba(test[FEATURES])[:,1]
    metrics = {"classification_report": classification_report(test["is_inactive"].astype(int), pred, output_dict=True, zero_division=0)}
    if test["is_inactive"].nunique() == 2:
        metrics["roc_auc"] = float(roc_auc_score(test["is_inactive"].astype(int), probability))
    return pipe, metrics, test.index
