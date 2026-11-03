# Dataset: UCI Online Retail II

## Selected source

We will use **Online Retail II**, published by the UCI Machine Learning Repository.

- Official dataset page: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Dataset DOI: https://doi.org/10.24432/C5CG6D
- Creator: Daqing Chen
- License: Creative Commons Attribution 4.0 International (CC BY 4.0)
- Coverage: 1 December 2009 to 9 December 2011
- Size: 1,067,371 transaction line-items
- Format: Excel workbook (`online_retail_II.xlsx`), approximately 43.5 MB
- Fields: Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, Country

The data represents transactions from a UK-based non-store online retailer selling giftware. It includes missing customer identifiers, cancellations (invoice numbers beginning with `C`), negative quantities/values, and other data-quality issues. These are analytical signals to investigate, not blindly discard.

## Download

From the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/download_data.py
```

The script downloads the official UCI ZIP archive and extracts the workbook to `data/raw/online_retail_II.xlsx`. The raw workbook is intentionally excluded from Git.

## Data dictionary

| Source column | Meaning | Notes |
|---|---|---|
| Invoice | Invoice identifier | Prefix `C` indicates a cancellation |
| StockCode | Product identifier | Treat as text; codes may contain letters |
| Description | Product description | May be missing |
| Quantity | Units on the invoice line | Negative values can represent returns/cancellations |
| InvoiceDate | Invoice timestamp | Parse as datetime |
| Price | Unit price | GBP |
| Customer ID | Customer identifier | Missing for some transactions |
| Country | Customer country | Categorical |

## Analytical handling principles

- Preserve a raw, immutable copy.
- Profile missing values, duplicates, cancellations, negative quantities and non-positive prices before choosing treatment.
- Separate revenue from refunds/returns where appropriate; document the business definition used.
- Exclude records without customer IDs only from customer-level analyses that require identity; retain them for appropriate aggregate sales analysis.
- Avoid data leakage: churn/inactivity labels and features must be defined using explicit observation and prediction windows.
- Treat monetary values as GBP and state this clearly in outputs.

## Attribution

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

This project uses the dataset under CC BY 4.0. Attribution must be retained in project documentation and any redistributed adaptations.
