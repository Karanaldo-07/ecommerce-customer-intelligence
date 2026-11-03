import pandas as pd
import pytest
from ecommerce_intel.data import clean_transactions, validate_transactions, customer_orders

@pytest.fixture
def sample():
    return pd.DataFrame({
        "invoice_no":["10001","10001","C10002","10003","10004"],
        "stock_code":["A","B","A","C","D"],
        "description":["one","two","one","three","four"],
        "quantity":[2,1,-1,1,1],
        "invoice_date":pd.to_datetime(["2011-01-01","2011-01-01","2011-01-02","2011-01-03","2011-01-04"]),
        "unit_price":[10,5,10,0,20],
        "customer_id":["1","1","1",None,"2"],
        "country":["UK","UK","UK","UK","France"],
    })

def test_clean_flags_sales_returns_and_cancellations(sample):
    cleaned = clean_transactions(sample)
    assert cleaned["is_valid_sale"].tolist() == [True, True, False, False, True]
    assert cleaned["is_cancellation"].sum() == 1
    assert cleaned["is_return_or_non_sale"].sum() == 2

def test_quality_counts(sample):
    cleaned = clean_transactions(sample)
    report = validate_transactions(cleaned)
    assert report["rows"] == 5
    assert report["valid_sale_lines"] == 3
    assert report["missing_customer_id"] == 1

def test_customer_orders_excludes_unidentified_and_invalid(sample):
    orders = customer_orders(clean_transactions(sample))
    assert len(orders) == 2
    assert orders["order_revenue"].sum() == 45

def test_missing_columns_raise():
    with pytest.raises(ValueError):
        clean_transactions(pd.DataFrame({"invoice_no":["1"]}))
