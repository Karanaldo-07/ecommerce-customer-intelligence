"""Leakage-aware customer inactivity dataset and baseline model comparison."""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, classification_report,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ["recency_days", "frequency_180d", "monetary_180d"]


def build_inactivity_dataset(df: pd.DataFrame, lookback_days: int = 180,
                             horizon_days: int = 90) -> pd.DataFrame:
    """Create monthly customer snapshots; label inactivity only in a future window.

    A customer is eligible at a snapshot if they purchased in the preceding
    lookback window. is_inactive=1 means no valid identified purchase in the
    subsequent horizon. Snapshots without a fully observed future horizon
    are excluded to avoid right-censoring.
    """
    sales = df.loc[df["is_valid_sale"] & df["customer_id"].notna()].copy()
    if sales.empty:
        return pd.DataFrame(columns=["customer_id", "observation_end", *FEATURES, "is_inactive"])
    sales["invoice_date"] = pd.to_datetime(sales["invoice_date"])
    orders = (sales.groupby(["customer_id", "invoice_no"], as_index=False)
              .agg(invoice_date=("invoice_date", "min"),
                   order_revenue=("line_revenue", "sum")))
    first_date = orders["invoice_date"].min().normalize()
    last_date = orders["invoice_date"].max().normalize()
    first_snapshot = first_date + pd.Timedelta(days=lookback_days)
    last_snapshot = last_date - pd.Timedelta(days=horizon_days)
    if first_snapshot > last_snapshot:
        return pd.DataFrame(columns=["customer_id", "observation_end", *FEATURES, "is_inactive"])
    snapshots = pd.date_range(first_snapshot.to_period("M").to_timestamp("M"),
                               last_snapshot.to_period("M").to_timestamp("M"), freq="ME")
    rows = []
    for snapshot in snapshots:
        feature_start = snapshot - pd.Timedelta(days=lookback_days)
        label_end = snapshot + pd.Timedelta(days=horizon_days)
        history = orders.loc[(orders["invoice_date"] > feature_start) &
                             (orders["invoice_date"] <= snapshot)]
        future = orders.loc[(orders["invoice_date"] > snapshot) &
                            (orders["invoice_date"] <= label_end)]
        if history.empty:
            continue
        grouped = history.groupby("customer_id").agg(
            last_purchase=("invoice_date", "max"),
            frequency_180d=("invoice_no", "nunique"),
            monetary_180d=("order_revenue", "sum"))
        grouped["recency_days"] = (snapshot - grouped["last_purchase"]).dt.days
        future_customers = set(future["customer_id"].unique())
        grouped["is_inactive"] = (~grouped.index.isin(future_customers)).astype(int)
        grouped["customer_id"] = grouped.index.astype(str)
        grouped["observation_end"] = snapshot
        rows.append(grouped.reset_index(drop=True)[
            ["customer_id", "observation_end", *FEATURES, "is_inactive"]])
    if not rows:
        return pd.DataFrame(columns=["customer_id", "observation_end", *FEATURES, "is_inactive"])
    return pd.concat(rows, ignore_index=True)


def train_inactivity_baseline(customer_features: pd.DataFrame, test_size: float = .25,
                              random_state: int = 42):
    """Compare logistic regression and random forest using chronological snapshots."""
    required = set(FEATURES + ["is_inactive", "observation_end"])
    missing = required - set(customer_features.columns)
    if missing:
        raise ValueError(f"Model input missing columns: {sorted(missing)}")
    data = customer_features.dropna(subset=["is_inactive", "observation_end"]).copy()
    data["observation_end"] = pd.to_datetime(data["observation_end"])
    if data["is_inactive"].nunique() != 2:
        raise ValueError("is_inactive must contain both classes (0 and 1)")
    dates = sorted(data["observation_end"].unique())
    if len(dates) < 2:
        raise ValueError("At least two distinct observation_end dates are required")
    cutoff_index = max(1, min(len(dates)-1, int(len(dates)*(1-test_size))))
    cutoff = dates[cutoff_index]
    train = data[data["observation_end"] < cutoff]
    test = data[data["observation_end"] >= cutoff]
    if train.empty or test.empty or train["is_inactive"].nunique() < 2:
        raise ValueError("Chronological split does not contain enough examples/classes")
    y_train, y_test = train["is_inactive"].astype(int), test["is_inactive"].astype(int)
    models = {
        "logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced"))]),
        "random_forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
                                               class_weight="balanced", random_state=random_state,
                                               n_jobs=-1))])
    }
    fitted, results = {}, {}
    for name, pipe in models.items():
        pipe.fit(train[FEATURES], y_train)
        pred = pipe.predict(test[FEATURES])
        probability = pipe.predict_proba(test[FEATURES])[:, 1]
        results[name] = {
            "precision": float(precision_score(y_test, pred, zero_division=0)),
            "recall": float(recall_score(y_test, pred, zero_division=0)),
            "f1": float(f1_score(y_test, pred, zero_division=0)),
            "classification_report": classification_report(y_test, pred, output_dict=True, zero_division=0),
            "roc_auc": float(roc_auc_score(y_test, probability)) if y_test.nunique() == 2 else None,
            "pr_auc": float(average_precision_score(y_test, probability)) if y_test.nunique() == 2 else None,
        }
        fitted[name] = pipe
    return fitted, {"cutoff": str(pd.Timestamp(cutoff).date()),
                    "train_rows": int(len(train)), "test_rows": int(len(test)),
                    "train_observation_end_max": str(train["observation_end"].max().date()),
                    "test_observation_end_min": str(test["observation_end"].min().date()),
                    "test_inactivity_rate": float(y_test.mean()), "models": results}, test.index
