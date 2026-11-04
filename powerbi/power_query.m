// Power BI Power Query helper
// 1. Copy the repository's dashboard_data folder to your computer.
// 2. Replace FolderPath below with the full path to that folder.
// 3. Create a Blank Query, open Advanced Editor, paste this code, and name it DashboardData.
// 4. Create one Reference query for each table using the examples in powerbi/README.md.

let
    FolderPath = "C:\\PATH\\TO\\ecommerce-customer-intelligence\\dashboard_data\\",
    LoadCsv = (FileName as text) as table =>
        Table.PromoteHeaders(
            Csv.Document(
                File.Contents(FolderPath & FileName),
                [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
            ),
            [PromoteAllScalars = true]
        ),
    MonthlyRevenue = LoadCsv("monthly_revenue.csv"),
    CountryPerformance = LoadCsv("country_performance.csv"),
    ProductPerformance = LoadCsv("product_performance.csv"),
    CustomerTypeSummary = LoadCsv("customer_type_summary.csv"),
    CustomerRevenueBands = LoadCsv("customer_revenue_bands.csv"),
    SegmentCounts = LoadCsv("segment_counts.csv"),
    CohortRetention = LoadCsv("cohort_retention.csv"),
    InactivityMonthly = LoadCsv("inactivity_monthly_summary.csv")
in
    [
        MonthlyRevenue = MonthlyRevenue,
        CountryPerformance = CountryPerformance,
        ProductPerformance = ProductPerformance,
        CustomerTypeSummary = CustomerTypeSummary,
        CustomerRevenueBands = CustomerRevenueBands,
        SegmentCounts = SegmentCounts,
        CohortRetention = CohortRetention,
        InactivityMonthly = InactivityMonthly
    ]
