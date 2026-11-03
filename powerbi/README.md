# Power BI Dashboard Guide

This folder contains the semantic model plan and DAX measures for the E-Commerce Customer Intelligence project. The validated CSV exports are generated under `data/processed/` by the **Build analytics outputs** GitHub Actions workflow.

## Import these tables

Use **Get Data → Text/CSV** and load the following files:

| Power BI table | Source file | Purpose |
|---|---|---|
| MonthlyRevenue | `eda_monthly_revenue.csv` | Monthly revenue and invoice trend |
| CountryPerformance | `eda_country_performance.csv` | Revenue by country |
| ProductPerformance | `eda_product_performance.csv` | Product sales ranking |
| CustomerSummary | `eda_customer_summary.csv` | Customer orders and lifetime revenue |
| CohortRetention | `eda_cohort_retention.csv` | Cohort month, age, retention |
| OrderValues | `eda_order_values.csv` | Invoice-level value distribution |
| InactivitySnapshots | `inactivity_training_data.csv` | Model features and observed inactivity label |

Import `customer_segments.csv` as CustomerSegments if segment-level reporting is desired. Treat the inactivity table as model-evaluation history, not as a live prediction feed.

## Recommended relationships

- CustomerSummary[customer_id] 1 → * InactivitySnapshots[customer_id]
- CustomerSummary[customer_id] 1 → * CustomerSegments[customer_id], if the customer segment file is loaded.
- Keep MonthlyRevenue, CountryPerformance, ProductPerformance, CohortRetention, and OrderValues as separate aggregate fact tables unless a shared date/product/country dimension is explicitly created. Do not create ambiguous many-to-many relationships.

## Suggested report pages

1. **Executive Overview:** revenue, invoices, average order value, identified customers, repeat-customer rate; monthly revenue trend.
2. **Revenue Drivers:** country revenue/share and top products by revenue/units.
3. **Customer Behaviour:** one-time vs repeat customers, lifetime revenue distribution, cohort retention heatmap.
4. **Inactivity Model:** inactive prevalence, model comparison, precision/recall/F1/ROC-AUC/PR-AUC, and a prominent warning that inactivity is a 90-day proxy.

## DAX measures

Copy measures from `measures.dax` after importing the matching tables. If a column name differs because Power BI adjusted it during import, update the expression to match the imported field name.

## Formatting and interpretation

- Currency: GBP (£), two decimal places.
- Rates: percentage, one decimal place.
- Dates: month-year.
- Display the dataset date range and refresh date.
- Do not label the model output as guaranteed churn. The label means no purchase in the next 90 days under the historical observation design.
- Do not sum customer counts across monthly snapshots; the same customer can appear more than once.
