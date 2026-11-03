"""Exploratory data analysis tables, charts, and factual summary."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from .data import customer_orders
from .analytics import monthly_revenue, country_performance, cohort_retention


def run_eda(df: pd.DataFrame, output_dir: str | Path, report_dir: str | Path) -> dict:
    """Create reproducible EDA tables and figures from cleaned transaction rows."""
    output_dir, report_dir = Path(output_dir), Path(report_dir)
    figures = report_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    sales = df.loc[df["is_valid_sale"]].copy()
    identified = sales.loc[sales["customer_id"].notna()].copy()
    orders = customer_orders(df)

    monthly = monthly_revenue(df)
    countries = country_performance(df)
    products = (sales.groupby("stock_code", as_index=False)
                .agg(description=("description", "first"), units_sold=("quantity", "sum"),
                     revenue=("line_revenue", "sum"), invoice_count=("invoice_no", "nunique"))
                .sort_values("revenue", ascending=False))
    order_values = (orders.groupby(["customer_id", "invoice_no"], as_index=False)
                    ["order_revenue"].sum())
    customer_summary = (orders.groupby("customer_id", as_index=False)
                        .agg(orders=("invoice_no", "nunique"),
                             lifetime_revenue=("order_revenue", "sum"),
                             last_purchase=("invoice_date", "max")))
    customer_summary["customer_type"] = customer_summary["orders"].map(
        lambda count: "Repeat" if count > 1 else "One-time"
    )
    cohorts = cohort_retention(df)

    monthly.to_csv(output_dir / "eda_monthly_revenue.csv", index=False)
    countries.to_csv(output_dir / "eda_country_performance.csv", index=False)
    products.to_csv(output_dir / "eda_product_performance.csv", index=False)
    order_values.to_csv(output_dir / "eda_order_values.csv", index=False)
    customer_summary.to_csv(output_dir / "eda_customer_summary.csv", index=False)
    cohorts.to_csv(output_dir / "eda_cohort_retention.csv", index=False)

    # Monthly revenue trend
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly["month"], monthly["revenue"], marker="o", linewidth=1.8)
    ax.set(title="Monthly Revenue Trend", xlabel="Month", ylabel="Revenue (GBP)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures / "monthly_revenue_trend.png", dpi=150)
    plt.close(fig)

    # Top countries
    top_countries = countries.head(10).sort_values("revenue")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_countries["country"], top_countries["revenue"])
    ax.set(title="Top 10 Countries by Revenue", xlabel="Revenue (GBP)", ylabel="Country")
    fig.tight_layout()
    fig.savefig(figures / "top_countries_revenue.png", dpi=150)
    plt.close(fig)

    # Top products
    top_products = products.head(10).sort_values("revenue")
    labels = top_products["stock_code"].astype(str)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(labels, top_products["revenue"])
    ax.set(title="Top 10 Products by Revenue", xlabel="Revenue (GBP)", ylabel="Stock code")
    fig.tight_layout()
    fig.savefig(figures / "top_products_revenue.png", dpi=150)
    plt.close(fig)

    # Order value distribution (clip display to 99th percentile, retain full CSV)
    fig, ax = plt.subplots(figsize=(10, 5))
    if not order_values.empty:
        upper = order_values["order_revenue"].quantile(0.99)
        ax.hist(order_values.loc[order_values["order_revenue"] <= upper, "order_revenue"], bins=50)
    ax.set(title="Order Value Distribution (up to 99th percentile)", xlabel="Order value (GBP)", ylabel="Orders")
    fig.tight_layout()
    fig.savefig(figures / "order_value_distribution.png", dpi=150)
    plt.close(fig)

    # Cohort retention heatmap, represented as a matrix
    if not cohorts.empty:
        matrix = cohorts.pivot(index="cohort_month", columns="cohort_index", values="retention_rate")
        fig, ax = plt.subplots(figsize=(12, 8))
        image = ax.imshow(matrix.values, aspect="auto", vmin=0, vmax=1)
        ax.set(title="Monthly Customer Cohort Retention", xlabel="Months Since First Purchase",
               ylabel="First Purchase Cohort")
        ax.set_xticks(range(len(matrix.columns)), labels=matrix.columns)
        ax.set_yticks(range(len(matrix.index)), labels=matrix.index.strftime("%Y-%m"))
        fig.colorbar(image, ax=ax, label="Retention rate")
        fig.tight_layout()
        fig.savefig(figures / "cohort_retention_heatmap.png", dpi=150)
        plt.close(fig)

    total_revenue = float(sales["line_revenue"].sum())
    total_orders = int(sales["invoice_no"].nunique())
    repeat_customers = int((customer_summary["orders"] > 1).sum())
    identified_customers = int(customer_summary["customer_id"].nunique())
    summary = {
        "valid_sale_lines": int(len(sales)),
        "identified_sale_lines": int(len(identified)),
        "total_revenue_gbp": round(total_revenue, 2),
        "unique_invoices_in_valid_sales": total_orders,
        "identified_customers": identified_customers,
        "repeat_customers": repeat_customers,
        "repeat_customer_rate": round(repeat_customers / identified_customers, 4) if identified_customers else None,
        "average_order_value_gbp": round(total_revenue / total_orders, 2) if total_orders else None,
        "top_country_by_revenue": str(countries.iloc[0]["country"]) if not countries.empty else None,
        "top_country_revenue_gbp": round(float(countries.iloc[0]["revenue"]), 2) if not countries.empty else None,
        "top_product_stock_code": str(products.iloc[0]["stock_code"]) if not products.empty else None,
        "top_product_revenue_gbp": round(float(products.iloc[0]["revenue"]), 2) if not products.empty else None,
    }
    (report_dir / "eda_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
