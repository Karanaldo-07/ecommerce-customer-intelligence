"""Reusable business analytics."""
import pandas as pd
from .data import customer_orders

def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    sales = df.loc[df["is_valid_sale"]].copy()
    sales["month"] = sales["invoice_date"].dt.to_period("M").dt.to_timestamp()
    return sales.groupby("month", as_index=False).agg(revenue=("line_revenue","sum"), orders=("invoice_no","nunique"), units=("quantity","sum"))

def country_performance(df: pd.DataFrame) -> pd.DataFrame:
    sales = df.loc[df["is_valid_sale"]]
    return (sales.groupby("country", as_index=False)
            .agg(revenue=("line_revenue","sum"), orders=("invoice_no","nunique"), customers=("customer_id","nunique"))
            .sort_values("revenue", ascending=False))

def build_rfm(df: pd.DataFrame, reference_date=None) -> pd.DataFrame:
    orders = customer_orders(df)
    if orders.empty:
        return pd.DataFrame(columns=["customer_id","recency_days","frequency","monetary"])
    reference = pd.Timestamp(reference_date) if reference_date is not None else orders["invoice_date"].max() + pd.Timedelta(days=1)
    rfm = orders.groupby("customer_id").agg(
        last_purchase=("invoice_date","max"),
        frequency=("invoice_no","nunique"),
        monetary=("order_revenue","sum"),
    )
    rfm["recency_days"] = (reference - rfm["last_purchase"]).dt.days
    return rfm.drop(columns="last_purchase").reset_index()[["customer_id","recency_days","frequency","monetary"]]

def cohort_retention(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly customer retention by first-purchase cohort."""
    orders = customer_orders(df)
    columns = ["cohort_month", "activity_month", "cohort_index", "customers", "cohort_size", "retention_rate"]
    if orders.empty:
        return pd.DataFrame(columns=columns)
    orders = orders[["customer_id", "invoice_date"]].drop_duplicates().copy()
    orders["activity_month"] = orders["invoice_date"].dt.to_period("M").dt.to_timestamp()
    first_purchase = orders.groupby("customer_id")["activity_month"].min().rename("cohort_month")
    orders = orders.join(first_purchase, on="customer_id")
    orders["cohort_index"] = (
        (orders["activity_month"].dt.year - orders["cohort_month"].dt.year) * 12
        + orders["activity_month"].dt.month - orders["cohort_month"].dt.month + 1
    )
    counts = (orders.groupby(["cohort_month", "activity_month", "cohort_index"])["customer_id"]
              .nunique().rename("customers").reset_index())
    sizes = counts.loc[counts["cohort_index"] == 1, ["cohort_month", "customers"]]
    sizes = sizes.rename(columns={"customers": "cohort_size"})
    result = counts.merge(sizes, on="cohort_month", how="left")
    result["retention_rate"] = result["customers"] / result["cohort_size"]
    return result[columns].sort_values(["cohort_month", "cohort_index"]).reset_index(drop=True)
