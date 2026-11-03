"""Interactive, privacy-conscious E-Commerce Customer Intelligence dashboard."""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "dashboard_data"

st.set_page_config(
    page_title="E-Commerce Intelligence | Retail Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background: #f5f7fb; }
[data-testid="stHeader"] { background: rgba(245,247,251,.88); }
.block-container { padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1500px; }
h1, h2, h3 { font-family: 'Manrope', sans-serif; color: #14213d; }
.hero { background: linear-gradient(115deg,#101d3a 0%,#173b67 58%,#176b78 100%);
        padding: 1.7rem 2rem; border-radius: 18px; color: white; margin-bottom: 1.25rem;
        box-shadow: 0 10px 28px rgba(16,29,58,.13); }
.hero h1 { color: white; font-size: 2rem; margin: 0 0 .35rem 0; }
.hero p { color: #d9e7f6; margin: 0; font-size: .96rem; }
.eyebrow { color: #9bd8d5; text-transform: uppercase; letter-spacing: .13em;
           font-size: .72rem; font-weight: 700; margin-bottom: .5rem; }
.kpi { background: white; border: 1px solid #e7ebf2; border-radius: 14px;
       padding: 1rem 1.15rem; box-shadow: 0 3px 12px rgba(21,39,71,.04); min-height: 112px; }
.kpi-label { color: #68758a; font-size: .78rem; font-weight: 600; margin-bottom: .4rem; }
.kpi-value { color: #14213d; font-family: 'Manrope',sans-serif; font-size: 1.65rem;
             font-weight: 800; line-height: 1.2; }
.kpi-note { color: #8490a3; font-size: .72rem; margin-top: .35rem; }
.section-note { background: #edf4fb; border-left: 4px solid #2c78a8; padding: .75rem 1rem;
                border-radius: 8px; color: #30445e; font-size: .88rem; margin: .5rem 0 1rem; }
.insight { background: white; border: 1px solid #e7ebf2; border-radius: 12px;
           padding: 1rem 1.1rem; height: 100%; }
.insight b { color: #173b67; }
div[data-testid="stTabs"] button { font-weight: 600; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #176b78; }
[data-testid="stSidebar"] { background: #eef2f8; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_csv(name, date_cols=()):
    path = DATA / name
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    for col in date_cols:
        if col in frame.columns:
            frame[col] = pd.to_datetime(frame[col], errors="coerce")
    return frame

@st.cache_data
def load_json(name):
    path = DATA / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def money(value, decimals=0):
    return f"£{value:,.{decimals}f}"

def kpi(label, value, note=""):
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>',
        unsafe_allow_html=True,
    )

def chart_style(fig, height=360):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
        font=dict(family="DM Sans", color="#334155"),
        margin=dict(l=12, r=12, t=55, b=12),
        title=dict(font=dict(size=16, color="#172b4d")),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#edf1f6", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig

monthly = load_csv("monthly_revenue.csv", ("month",))
countries = load_csv("country_performance.csv")
products = load_csv("product_performance.csv")
customers = load_csv("customer_type_summary.csv")
bands = load_csv("customer_revenue_bands.csv")
cohorts = load_csv("cohort_retention.csv", ("cohort_month", "activity_month"))
segments = load_csv("segment_counts.csv")
snapshots = load_csv("inactivity_monthly_summary.csv", ("observation_end",))
quality = load_json("data_quality.json")
summary = load_json("eda_summary.json")
model = load_json("model_evaluation.json")

st.markdown("""
<div class="hero">
  <div class="eyebrow">Retail performance • Customer intelligence • Predictive analytics</div>
  <h1>E-Commerce Intelligence</h1>
  <p>Understand revenue drivers, customer value, retention patterns and future inactivity — all in one place.</p>
</div>
""", unsafe_allow_html=True)

required = {
    "monthly revenue": monthly, "country performance": countries,
    "product performance": products, "customer summary": customers,
    "cohort retention": cohorts,
}
missing = [name for name, frame in required.items() if frame.empty]
if missing:
    st.error("Dashboard data is incomplete: " + ", ".join(missing))
    st.info("Run the Build analytics outputs workflow in GitHub, then reboot this app.")
    st.stop()

# ---------- Sidebar filters ----------
with st.sidebar:
    st.markdown("## Dashboard controls")
    st.caption("Filter the revenue view. Customer and model summaries use the full identified-customer history.")
    min_date = monthly["month"].min().date()
    max_date = monthly["month"].max().date()
    date_range = st.date_input(
        "Revenue date range", value=(min_date, max_date),
        min_value=min_date, max_value=max_date,
        help="Applies to monthly revenue KPIs and trend.",
    )
    st.divider()
    country_options = ["All countries"] + sorted(countries["country"].dropna().astype(str).unique())
    selected_country = st.selectbox("Country detail", country_options)
    top_n = st.slider("Number of products to show", 5, 20, 10)
    st.divider()
    st.markdown("**Dataset**")
    st.caption("UCI Online Retail II")
    st.caption("1 Dec 2009 – 9 Dec 2011")
    st.caption("Currency: GBP (£)")
    st.caption("Customer-level records are not published in this dashboard.")

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = pd.Timestamp(min_date), pd.Timestamp(max_date)
rev = monthly[monthly["month"].between(start, end)].copy()
if rev.empty:
    st.warning("No monthly revenue is available for this date range.")
    st.stop()

revenue = float(rev["revenue"].sum())
invoice_count = int(rev["orders"].sum())
units = int(rev["units_sold"].sum()) if "units_sold" in rev.columns else 0
aov = revenue / invoice_count if invoice_count else 0
repeat_rate = float(summary.get("repeat_customer_rate", 0))
identified = int(summary.get("identified_customers", 0))
repeat_customers = int(summary.get("repeat_customers", 0))
total_revenue = float(summary.get("total_revenue_gbp", 0))
top_country = str(summary.get("top_country_by_revenue", "United Kingdom"))
top_country_revenue = float(summary.get("top_country_revenue_gbp", 0))
top_product = products.sort_values("revenue", ascending=False).iloc[0]

st.markdown("### Performance snapshot")
st.caption(f"Revenue period: {start:%d %b %Y} — {end:%d %b %Y}")
cols = st.columns(4)
with cols[0]: kpi("NET SALES REVENUE", money(revenue), "Valid sale lines only")
with cols[1]: kpi("INVOICES", f"{invoice_count:,}", "Distinct valid-sale invoices")
with cols[2]: kpi("AVERAGE ORDER VALUE", money(aov, 2), "Revenue ÷ invoices")
with cols[3]: kpi("REPEAT CUSTOMER RATE", f"{repeat_rate:.1%}", f"{repeat_customers:,} of {identified:,} identified customers")

tab_overview, tab_revenue, tab_customer, tab_model, tab_quality = st.tabs([
    "  Overview  ", "  Revenue drivers  ", "  Customer intelligence  ",
    "  Inactivity model  ", "  Data quality  ",
])

# ---------- Overview ----------
with tab_overview:
    st.markdown("### Revenue trajectory")
    left, right = st.columns([1.8, 1])
    with left:
        fig = px.area(rev, x="month", y="revenue", markers=True,
                      labels={"month":"Month","revenue":"Revenue (GBP)"},
                      title="Monthly revenue")
        fig.update_traces(line_color="#176b9a", fillcolor="rgba(23,107,154,.12)")
        st.plotly_chart(chart_style(fig, 390), use_container_width=True)
    with right:
        st.markdown("#### At a glance")
        kpi("IDENTIFIED CUSTOMERS", f"{identified:,}", "Customers with a known ID")
        st.write("")
        kpi("TOP REVENUE MARKET", top_country, f"{top_country_revenue / total_revenue:.1%} of total sales" if total_revenue else "")
        st.write("")
        kpi("TOP PRODUCT", str(top_product["description"])[:32], money(float(top_product["revenue"])) + " revenue")
    a, b = st.columns(2)
    with a:
        top_products = products.nlargest(top_n, "revenue").sort_values("revenue")
        fig = px.bar(top_products, x="revenue", y="description", orientation="h",
                     hover_data=["stock_code","units_sold","invoice_count"],
                     labels={"revenue":"Revenue (GBP)","description":"Product"},
                     title=f"Top {top_n} products by revenue")
        fig.update_traces(marker_color="#2b8290")
        st.plotly_chart(chart_style(fig, 440), use_container_width=True)
    with b:
        top_countries = countries.nlargest(10, "revenue").sort_values("revenue")
        fig = px.bar(top_countries, x="revenue", y="country", orientation="h",
                     labels={"revenue":"Revenue (GBP)","country":"Country"},
                     title="Top 10 countries")
        fig.update_traces(marker_color="#4c78a8")
        st.plotly_chart(chart_style(fig, 440), use_container_width=True)
    st.markdown("#### Business takeaways")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="insight"><b>Market concentration</b><br>{top_country} contributes <b>{top_country_revenue / total_revenue:.1%}</b> of recorded valid-sale revenue. Consider testing expansion carefully before assuming other markets can scale similarly.</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="insight"><b>Customer loyalty</b><br><b>{repeat_rate:.1%}</b> of identified customers made repeat purchases. Retention campaigns should focus on converting one-time buyers into second-time buyers.</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="insight"><b>Product opportunity</b><br><b>{top_product["description"]}</b> is the leading product by revenue. Check margin and stock availability before prioritising promotion.</div>', unsafe_allow_html=True)

# ---------- Revenue drivers ----------
with tab_revenue:
    st.markdown("### Where does revenue come from?")
    country_view = countries if selected_country == "All countries" else countries[countries["country"] == selected_country]
    if country_view.empty:
        st.info("No records for the selected country.")
    else:
        row = country_view.sort_values("revenue", ascending=False).iloc[0]
        c1, c2, c3 = st.columns(3)
        with c1: kpi("MARKET REVENUE", money(float(country_view["revenue"].sum())), selected_country)
        with c2: kpi("INVOICES", f"{int(country_view['orders'].sum()):,}", "Across selected market(s)")
        with c3: kpi("CUSTOMERS", f"{int(country_view['customers'].sum()):,}", "Identified customers")
        fig = px.bar(country_view.nlargest(20, "revenue").sort_values("revenue"),
                     x="revenue", y="country", orientation="h",
                     hover_data=["orders","customers"],
                     labels={"revenue":"Revenue (GBP)","country":"Country"},
                     title="Country revenue ranking")
        fig.update_traces(marker_color="#176b9a")
        st.plotly_chart(chart_style(fig, 500), use_container_width=True)
        st.download_button("⬇ Download country performance (CSV)",
            country_view.to_csv(index=False).encode("utf-8"),
            file_name="country_performance.csv", mime="text/csv")
    st.markdown("### Product performance")
    product_view = products.nlargest(top_n, "revenue")
    st.dataframe(product_view.rename(columns={
        "stock_code":"Product code","description":"Product","units_sold":"Units sold",
        "revenue":"Revenue (GBP)","invoice_count":"Invoices"
    }).style.format({"Revenue (GBP)":"£{:,.2f}"}), use_container_width=True, hide_index=True)
    st.download_button("⬇ Download product performance (CSV)",
        products.to_csv(index=False).encode("utf-8"),
        file_name="product_performance.csv", mime="text/csv")

# ---------- Customer intelligence ----------
with tab_customer:
    st.markdown("### Customer mix and value")
    st.markdown('<div class="section-note">Customer metrics use only transactions with a known Customer ID. Revenue from unidentified customers is included in total sales but excluded from customer-level summaries.</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        fig = px.pie(customers, names="customer_type", values="customers", hole=.58,
                     title="One-time vs repeat customers",
                     color_discrete_sequence=["#9bb6cc","#176b78"])
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(chart_style(fig, 370), use_container_width=True)
    with b:
        fig = px.bar(bands, x="revenue_band", y="customers",
                     labels={"revenue_band":"Lifetime revenue band (GBP)","customers":"Customers"},
                     title="Customer lifetime revenue distribution")
        fig.update_traces(marker_color="#4c78a8")
        st.plotly_chart(chart_style(fig, 370), use_container_width=True)
    st.markdown("### RFM segments")
    st.caption("RFM groups customers using recency (how recently they purchased), frequency (how often), and monetary value (how much they spent). These are descriptive segments, not predictive labels.")
    if not segments.empty:
        seg = segments.sort_values("customers", ascending=True)
        fig = px.bar(seg, x="customers", y="segment", orientation="h",
                     labels={"customers":"Customers","segment":"Segment"},
                     title="Customer count by segment")
        fig.update_traces(marker_color="#2b8290")
        st.plotly_chart(chart_style(fig, 350), use_container_width=True)
    st.markdown("### Cohort retention")
    st.caption("Each row represents customers grouped by their first purchase month. Month 0 is the acquisition month; later columns show the share who returned.")
    matrix = cohorts.pivot_table(index="cohort_month", columns="cohort_index",
                                 values="retention_rate", aggfunc="mean").sort_index()
    matrix.index = pd.to_datetime(matrix.index).strftime("%b %Y")
    fig = px.imshow(matrix, aspect="auto", zmin=0, zmax=1,
                    color_continuous_scale="Teal",
                    labels={"x":"Months since first purchase","y":"Acquisition cohort","color":"Retention"},
                    title="Monthly cohort retention heatmap")
    fig.update_layout(coloraxis_colorbar=dict(tickformat=".0%"))
    st.plotly_chart(chart_style(fig, max(400, min(720, 25 * len(matrix)))), use_container_width=True)
    st.download_button("⬇ Download cohort retention (CSV)",
        cohorts.to_csv(index=False).encode("utf-8"),
        file_name="cohort_retention.csv", mime="text/csv")

# ---------- Model ----------
with tab_model:
    st.markdown("### 90-day customer inactivity model")
    st.markdown('<div class="section-note"><b>Important:</b> Inactivity means no recorded purchase in the next 90 days. It is an early-warning proxy, not proof that a customer has permanently churned.</div>', unsafe_allow_html=True)
    if model.get("status") != "trained":
        st.warning("Model evaluation is not available.")
    else:
        m1, m2, m3 = st.columns(3)
        with m1: kpi("TEST SNAPSHOTS", f"{int(model.get('test_rows',0)):,}", "Chronological holdout")
        with m2: kpi("INACTIVITY PREVALENCE", f"{float(model.get('test_inactivity_rate',0)):.1%}", "Share labelled inactive")
        with m3: kpi("HOLDOUT CUTOFF", str(model.get("cutoff","—")), "Time-based train/test split")
        rows = []
        for name, metrics in model.get("models", {}).items():
            rows.append({"Model":name.replace("_"," ").title(),
                         "Precision":metrics.get("precision",0),"Recall":metrics.get("recall",0),
                         "F1":metrics.get("f1",0),"ROC-AUC":metrics.get("roc_auc",0),
                         "PR-AUC":metrics.get("pr_auc",0)})
        scores = pd.DataFrame(rows)
        if not scores.empty:
            fig = px.bar(scores.melt(id_vars="Model",var_name="Metric",value_name="Score"),
                         x="Metric",y="Score",color="Model",barmode="group",
                         range_y=[0,1],title="Model comparison on unseen later-period data",
                         color_discrete_sequence=["#176b9a","#e09f3e"])
            st.plotly_chart(chart_style(fig, 400), use_container_width=True)
            st.dataframe(scores.style.format({c:"{:.3f}" for c in scores.columns if c!="Model"}),
                         use_container_width=True, hide_index=True)
            best = scores.sort_values("F1",ascending=False).iloc[0]
            st.markdown(f'<div class="insight"><b>Interpretation</b><br>{best["Model"]} has the higher F1 score ({best["F1"]:.3f}) in this evaluation. Recall measures how many actually inactive snapshots are detected; precision measures how many flagged snapshots are truly inactive. Choose a decision threshold based on the cost of missed customers versus unnecessary outreach.</div>', unsafe_allow_html=True)
        if not snapshots.empty:
            fig = px.line(snapshots.sort_values("observation_end"), x="observation_end",
                          y="inactive_share", markers=True,
                          labels={"observation_end":"Snapshot month","inactive_share":"Inactive share"},
                          title="Observed inactivity rate by snapshot month")
            fig.update_traces(line_color="#b56576")
            fig.update_yaxes(tickformat=".0%")
            st.plotly_chart(chart_style(fig, 370), use_container_width=True)
        st.caption("Models compared: Logistic Regression and Random Forest. Features use a 180-day lookback; the target looks 90 days ahead. Results are historical and may not generalise to current customers.")

# ---------- Data quality ----------
with tab_quality:
    st.markdown("### Trust and data coverage")
    q1, q2, q3, q4 = st.columns(4)
    with q1: kpi("RAW ROWS", f"{int(quality.get('rows',0)):,}", "Original workbook rows")
    with q2: kpi("VALID SALE LINES", f"{int(quality.get('valid_sale_lines',0)):,}", "Included in sales analysis")
    with q3: kpi("MISSING CUSTOMER ID", f"{int(quality.get('missing_customer_id',0)):,}", "Customer analysis limitation")
    with q4: kpi("DUPLICATE-LIKE ROWS", f"{int(quality.get('duplicate_rows',0)):,}", "Preserved for audit")
    q5, q6 = st.columns(2)
    with q5: kpi("CANCELLATIONS", f"{int(quality.get('cancellations',0)):,}", "Excluded from valid-sale revenue")
    with q6: kpi("NON-SALE LINES", f"{int(quality.get('non_sale_lines',0)):,}", "Excluded from valid-sale revenue")
    st.markdown("#### Data handling notes")
    st.markdown("""
    - Duplicate-looking transaction rows are **retained**, not silently deleted.
    - Cancellation invoices and non-sale/return lines are excluded from valid-sale revenue.
    - Transactions without a Customer ID remain in total sales where they qualify as valid sales, but are excluded from customer segmentation and retention analysis.
    - The source covers a historical period; this dashboard is an analytical portfolio exercise, not a live retailer feed.
    """)
    st.caption(f"Source transaction period: {quality.get('date_min','n/a')} to {quality.get('date_max','n/a')}")
    quality_rows = pd.DataFrame([
        {"Check":"Raw rows","Count":quality.get("rows",0)},
        {"Check":"Valid sale lines","Count":quality.get("valid_sale_lines",0)},
        {"Check":"Missing customer IDs","Count":quality.get("missing_customer_id",0)},
        {"Check":"Duplicate-looking rows","Count":quality.get("duplicate_rows",0)},
        {"Check":"Cancellation invoices","Count":quality.get("cancellations",0)},
        {"Check":"Non-sale lines","Count":quality.get("non_sale_lines",0)},
    ])
    st.dataframe(quality_rows, use_container_width=True, hide_index=True)
    st.download_button("⬇ Download data quality summary (CSV)",
        quality_rows.to_csv(index=False).encode("utf-8"),
        file_name="data_quality_summary.csv", mime="text/csv")

st.divider()
st.markdown(
    "<div style='text-align:center;color:#8490a3;font-size:.8rem'>"
    "E-Commerce Customer Intelligence · Independent portfolio project by Karan Bhise · "
    "Source: UCI Online Retail II · Currency: GBP</div>",
    unsafe_allow_html=True,
)
