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
