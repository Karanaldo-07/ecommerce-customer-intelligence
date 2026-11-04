# Power BI Executive Dashboard

Build a report from the **privacy-safe aggregate CSVs** in `dashboard_data/`. No customer IDs, invoice IDs, raw transactions or row-level model snapshots are required.

## 1. Refresh and import

Run the GitHub Actions workflow **Build analytics outputs**. It downloads UCI Online Retail II, rebuilds analysis, validates the public aggregates, and commits refreshed files to `dashboard_data/`.

For a faster import, use [`power_query.m`](power_query.m): copy the `dashboard_data/` folder locally, create a Blank Query in Power Query, paste the script into Advanced Editor, and replace `FolderPath` with your local folder path. Name the query `DashboardData`. Then create eight Reference queries and set each formula to `= DashboardData[MonthlyRevenue]`, `= DashboardData[CountryPerformance]`, `= DashboardData[ProductPerformance]`, `= DashboardData[CustomerTypeSummary]`, `= DashboardData[CustomerRevenueBands]`, `= DashboardData[SegmentCounts]`, `= DashboardData[CohortRetention]`, or `= DashboardData[InactivityMonthly]` respectively. Rename each reference query to the table name shown below.\n\nAlternatively, choose **Home → Get data → Text/CSV** and import each CSV individually:

| Power BI table | CSV | Purpose |
|---|---|---|
| MonthlyRevenue | monthly_revenue.csv | Monthly revenue, invoices and units |
| CountryPerformance | country_performance.csv | Country revenue, invoices and identified customer counts |
| ProductPerformance | product_performance.csv | Product revenue and volume |
| CustomerTypeSummary | customer_type_summary.csv | One-time vs repeat aggregates |
| CustomerRevenueBands | customer_revenue_bands.csv | Customer lifetime revenue bands |
| SegmentCounts | segment_counts.csv | RFM segment counts |
| CohortRetention | cohort_retention.csv | Retention by cohort and cohort age |
| InactivityMonthly | inactivity_monthly_summary.csv | Monthly aggregate inactivity rate |

Optional JSON files: `eda_summary.json`, `data_quality.json`, `model_evaluation.json`. Import through **Get data → JSON** if needed.

## 2. Data model and data types

These tables have different aggregation grains. Keep them as separate summary/fact tables; do not join them directly or sum customer counts across time. No customer-level relationship is required.

Set month/date fields to Date; revenue to Decimal number formatted as GBP; retention/inactivity shares to Decimal number formatted as Percentage; counts and cohort index to Whole number.

## 3. Report pages

### Page 1 — Executive overview
- KPI cards: Total Revenue GBP, Total Invoices, Average Order Value GBP, Units Sold, Repeat Customer Rate.
- Line: MonthlyRevenue[month] by Total Revenue GBP.
- Bar: CountryPerformance[country] by Country Revenue GBP (Top 10).
- Bar: ProductPerformance[description] by Product Revenue GBP (Top 10).
- Month slicer for the monthly trend.

### Page 2 — Revenue drivers
- Country revenue and invoice ranking.
- Product revenue and units sold.
- Country and product aggregates represent the full historical period; a monthly slicer only filters MonthlyRevenue.

### Page 3 — Customer intelligence
- Donut: CustomerTypeSummary[customer_type] by Customers.
- Bar: CustomerRevenueBands[revenue_band] by Customers.
- Bar: SegmentCounts[segment] by Customers.
- Matrix: CohortRetention[cohort_month] rows, [cohort_index] columns, Cohort Retention % values. Format as percentage with conditional background colour.

### Page 4 — Inactivity monitoring
- Line: InactivityMonthly[observation_end] by Monthly Inactivity Rate.
- Cards: latest inactivity rate and total snapshot count.
- Prominent note: “Inactivity means no purchase in the next 90 days. It is a historical proxy, not permanent churn or a live customer score.”

### Page 5 — Data quality
Use DataQuality JSON for raw rows, valid sale lines, missing customer IDs, duplicate-looking rows, cancellations and non-sale lines.

## 4. DAX and theme

Use `measures.dax` for measures matching the aggregate CSV schemas. Import `theme.json` using Power BI View → Themes → Browse for themes.

## 5. Interpretation limits

- UCI Online Retail II covers 1 December 2009 to 9 December 2011; this is not a live retailer feed.
- Valid-sale revenue includes eligible sales even when Customer ID is missing. Customer metrics include identified customers only.
- Duplicate-looking rows were retained for audit rather than automatically deleted.
- Country, product and customer summary tables are aggregate historical totals.
- Compare cohorts at the same age; newer cohorts have shorter observation histories.
- InactivityMonthly is a snapshot-level rate, not a count of unique inactive customers.
- No Power BI binary report is committed. Save the finished report as `.pbix` after building the pages.
