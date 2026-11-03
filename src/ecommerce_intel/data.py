"""Loading, cleaning, and validation for UCI Online Retail II."""
from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"]
COLUMN_MAP = {"Invoice":"invoice_no","StockCode":"stock_code","Description":"description","Quantity":"quantity","InvoiceDate":"invoice_date","Price":"unit_price","Customer ID":"customer_id","Country":"country"}

def load_retail_workbook(path: str | Path, sheet_name: int | str | None = None) -> pd.DataFrame:
    """Load both yearly sheets by default, or one explicitly requested sheet."""
    frames = pd.read_excel(path, sheet_name=sheet_name)
    if isinstance(frames, dict):
        for name, frame in frames.items():
            missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
            if missing:
                raise ValueError(f"Sheet {name!r} is missing required columns: {missing}")
        frame = pd.concat(frames.values(), ignore_index=True)
    else:
        frame = frames
        missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
        if missing:
            raise ValueError(f"Dataset is missing required columns: {missing}")
    return frame.rename(columns=COLUMN_MAP)

def clean_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    """Standardize records while preserving returns/cancellations for audit."""
    df = frame.copy()
    required = set(COLUMN_MAP.values())
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Input is missing required columns: {missing}")
    df["invoice_no"] = df["invoice_no"].astype("string").str.strip()
    df["stock_code"] = df["stock_code"].astype("string").str.strip()
    df["customer_id"] = df["customer_id"].astype("string").str.replace(r"\\.0$", "", regex=True)
    df["customer_id"] = df["customer_id"].replace({"<NA>": pd.NA, "nan": pd.NA, "None": pd.NA})
    df["description"] = df["description"].astype("string").str.strip()
    df["country"] = df["country"].astype("string").str.strip()
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["is_cancellation"] = df["invoice_no"].str.startswith("C", na=False)
    df["is_return_or_non_sale"] = df["quantity"].le(0) | df["unit_price"].le(0)
    df["line_revenue"] = df["quantity"] * df["unit_price"]
    df["is_valid_sale"] = (
        ~df["is_cancellation"] & ~df["is_return_or_non_sale"]
        & df["invoice_date"].notna() & df["quantity"].notna()
        & df["unit_price"].notna() & df["invoice_no"].notna()
    )
    return df.reset_index(drop=True)

def validate_transactions(df: pd.DataFrame) -> dict:
    """Return transparent quality counts; never silently discard questionable rows."""
    return {
        "rows": int(len(df)),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_customer_id": int(df["customer_id"].isna().sum()),
        "missing_invoice_date": int(df["invoice_date"].isna().sum()),
        "cancellations": int(df["is_cancellation"].sum()),
        "non_sale_lines": int(df["is_return_or_non_sale"].sum()),
        "valid_sale_lines": int(df["is_valid_sale"].sum()),
        "date_min": str(df["invoice_date"].min()) if df["invoice_date"].notna().any() else None,
        "date_max": str(df["invoice_date"].max()) if df["invoice_date"].notna().any() else None,
    }

def customer_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate valid identified sales to one row per customer and invoice."""
    sales = df.loc[df["is_valid_sale"] & df["customer_id"].notna()].copy()
    return (sales.groupby(["customer_id", "invoice_no", "invoice_date", "country"], as_index=False)
            .agg(order_revenue=("line_revenue", "sum"), items=("quantity", "sum")))
