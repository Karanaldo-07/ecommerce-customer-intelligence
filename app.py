"""Interactive Streamlit dashboard for validated UCI Online Retail II outputs."""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA, REPORTS = ROOT / "dashboard_data", ROOT / "dashboard_data"
st.set_page_config(page_title="E-Commerce Customer Intelligence", page_icon="📊", layout="wide")

@st.cache_data
def csv(name, dates=()):
    path = DATA / name
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    for col in dates:
        if col in frame:
            frame[col] = pd.to_datetime(frame[col], errors="coerce")
    return frame

@st.cache_data
def report(name):
    path = REPORTS / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

monthly = csv("monthly_revenue.csv", ("month",))
countries = csv("country_performance.csv")
products = csv("product_performance.csv")
customers = csv("customer_type_summary.csv")
cohorts = csv("cohort_retention.csv", ("cohort_month", "activity_month"))
segments = csv("segment_counts.csv")
snapshots = csv("inactivity_monthly_summary.csv", ("observation_end",))
quality, summary, model = report("data_quality.json"), report("eda_summary.json"), report("model_evaluation.json")

st.title("E-Commerce Customer Intelligence")
st.caption("UCI Online Retail II · Revenue analytics · Customer behaviour · 90-day inactivity baseline")
required = {"monthly revenue": monthly, "country performance": countries, "product performance": products,
            "customer summary": customers, "cohort retention": cohorts}
missing = [name for name, frame in required.items() if frame.empty]
if missing:
    st.error("Missing dashboard datasets: " + ", ".join(missing))
    st.markdown("Run the Build analytics outputs workflow; its final step publishes aggregate-only dashboard_data files to the repository. Restart the app after the workflow completes.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    options = ["All countries"] + sorted(countries["country"].dropna().unique().tolist())
    selected_country = st.selectbox("Country", options)
    min_date, max_date = monthly["month"].min().date(), monthly["month"].max().date()
    period = st.date_input("Revenue period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    st.caption("The period filter applies to revenue trend and KPIs. Customer and model metrics use the full history.")

rev = monthly.copy()
if isinstance(period, (tuple, list)) and len(period) == 2:
    rev = rev[rev["month"].between(pd.Timestamp(period[0]), pd.Timestamp(period[1]))]
country_view = countries if selected_country == "All countries" else countries[countries["country"] == selected_country]
revenue = float(rev["revenue"].sum())
invoice_count = int(rev["orders"].sum())
aov = revenue / invoice_count if invoice_count else 0
repeat_rate = float(summary.get("repeat_customer_rate", 0))
k = st.columns(4)
k[0].metric("Revenue (GBP)", f"£{revenue:,.0f}")
k[1].metric("Invoices", f"{invoice_count:,}")
k[2].metric("Average order value", f"£{aov:,.2f}")
k[3].metric("Repeat-customer rate", f"{repeat_rate:.1%}")

overview, drivers, customer, model_tab, quality_tab = st.tabs(
    ["Executive overview", "Revenue drivers", "Customer behaviour", "Inactivity model", "Data quality"])
with overview:
    left, right = st.columns([1.7, 1])
    with left:
        st.plotly_chart(px.line(rev, x="month", y="revenue", markers=True,
            labels={"month":"Month","revenue":"Revenue (GBP)"}, title="Monthly revenue"), use_container_width=True)
    with right:
        st.metric("Identified customers", f"{summary.get('identified_customers', 0):,}")
        st.metric("Repeat customers", f"{summary.get('repeat_customers', 0):,}")
        total = float(summary.get("total_revenue_gbp", 1))
        uk = float(summary.get("top_country_revenue_gbp", 0))
        st.metric("UK share of revenue", f"{uk/total:.1%}")
        st.info("Revenue includes valid sale lines. Customer metrics exclude rows without Customer ID.")
    top = products.nlargest(10, "revenue").sort_values("revenue")
    st.plotly_chart(px.bar(top, x="revenue", y="description", orientation="h",
        hover_data=["stock_code","units_sold","invoice_count"],
        labels={"revenue":"Revenue (GBP)","description":"Product"}, title="Top 10 products"), use_container_width=True)

with drivers:
    st.plotly_chart(px.bar(country_view.head(20).sort_values("revenue"), x="revenue", y="country",
        orientation="h", hover_data=["orders","customers"], labels={"revenue":"Revenue (GBP)"},
        title="Country performance"), use_container_width=True)
    st.dataframe(country_view, use_container_width=True, hide_index=True)
    st.subheader("Top products")
    st.dataframe(products.nlargest(25, "revenue"), use_container_width=True, hide_index=True)

with customer:
    a, b = st.columns(2)
    types = customers["customer_type"].value_counts().rename_axis("customer_type").reset_index(name="customers")
    a.plotly_chart(px.pie(types, names="customer_type", values="customers", hole=.45,
                          title="One-time vs repeat customers"), use_container_width=True)
    b.plotly_chart(px.histogram(customers, x="lifetime_revenue", nbins=50,
                                title="Lifetime revenue distribution",
                                labels={"lifetime_revenue":"Revenue (GBP)"}), use_container_width=True)
    matrix = cohorts.pivot(index="cohort_month", columns="cohort_index", values="retention_rate")
    st.plotly_chart(px.imshow(matrix, aspect="auto", zmin=0, zmax=1, color_continuous_scale="Blues",
        labels={"x":"Months since first purchase","y":"Cohort month","color":"Retention"},
        title="Cohort retention heatmap"), use_container_width=True)
    if not segments.empty:
        counts = segments["segment"].value_counts().rename_axis("segment").reset_index(name="customers")
        st.plotly_chart(px.bar(counts, x="segment", y="customers", title="RFM customer segments"),
                        use_container_width=True)

with model_tab:
    st.subheader("90-day inactivity baseline")
    if model.get("status") != "trained":
        st.warning("Model evaluation is not available in this report bundle.")
    else:
        st.warning("The target means no purchase in the next 90 days. This is an inactivity proxy, not permanent churn.")
        st.caption(f"Chronological holdout cutoff: {model.get('cutoff')}. Test snapshots: {model.get('test_rows', 0):,}. Inactivity prevalence: {model.get('test_inactivity_rate', 0):.1%}.")
        rows = [{"Model": name.replace("_"," ").title(), "Precision": m["precision"], "Recall": m["recall"],
                 "F1": m["f1"], "ROC-AUC": m["roc_auc"], "PR-AUC": m["pr_auc"]}
                for name,m in model.get("models",{}).items()]
        scores = pd.DataFrame(rows)
        st.dataframe(scores.style.format({col:"{:.3f}" for col in scores.columns if col != "Model"}),
                     use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(scores.melt(id_vars="Model",var_name="Metric",value_name="Score"),
            x="Metric",y="Score",color="Model",barmode="group",range_y=[0,1],
            title="Chronological holdout model comparison"), use_container_width=True)
        if not snapshots.empty:
            by_month = snapshots.groupby("observation_end",as_index=False)["is_inactive"].mean()
            st.plotly_chart(px.line(by_month,x="observation_end",y="is_inactive",markers=True,
                labels={"observation_end":"Observation month","is_inactive":"Inactive share"},
                title="Inactivity rate by snapshot month"), use_container_width=True)

with quality_tab:
    q = st.columns(4)
    q[0].metric("Raw rows", f"{quality.get('rows',0):,}")
    q[1].metric("Valid sale lines", f"{quality.get('valid_sale_lines',0):,}")
    q[2].metric("Missing customer IDs", f"{quality.get('missing_customer_id',0):,}")
    q[3].metric("Duplicate-looking rows", f"{quality.get('duplicate_rows',0):,}")
    q2 = st.columns(2)
    q2[0].metric("Cancellation invoices", f"{quality.get('cancellations',0):,}")
    q2[1].metric("Non-sale lines", f"{quality.get('non_sale_lines',0):,}")
    st.caption(f"Source period: {quality.get('date_min','n/a')} to {quality.get('date_max','n/a')}")
    st.info("Duplicate-looking rows are retained for audit. Cancellations and non-sale lines are excluded from valid-sale revenue.")

st.divider()
st.caption("Independent portfolio project by Karan Bhise · UCI Online Retail II · Currency: GBP")
