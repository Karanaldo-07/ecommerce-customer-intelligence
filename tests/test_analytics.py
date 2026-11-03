import pandas as pd
from ecommerce_intel.analytics import monthly_revenue, build_rfm
from ecommerce_intel.segmentation import segment_customers

def transactions():
    return pd.DataFrame({
        "invoice_no":["1","1","2","3"], "stock_code":["A","B","A","A"],
        "description":["a","b","a","a"], "quantity":[1,2,1,1],
        "invoice_date":pd.to_datetime(["2011-01-01","2011-01-01","2011-02-01","2011-02-02"]),
        "unit_price":[10,5,10,20], "customer_id":["10","10","10","20"],
        "country":["UK"]*4,
    })

def test_monthly_revenue_totals():
    df=transactions()
    df["is_valid_sale"]=True
    df["line_revenue"]=df.quantity*df.unit_price
    result=monthly_revenue(df)
    assert result["revenue"].tolist()==[20,30]

def test_rfm_order_frequency_and_monetary():
    df=transactions()
    df["is_valid_sale"]=True
    df["line_revenue"]=df.quantity*df.unit_price
    result=build_rfm(df, reference_date="2011-02-03")
    row=result.set_index("customer_id").loc["10"]
    assert row["frequency"]==2
    assert row["monetary"]==35
    assert row["recency_days"]==2

def test_segmentation_adds_labels():
    rfm=pd.DataFrame({"customer_id":["a","b","c","d"],"recency_days":[1,10,20,30],"frequency":[10,8,2,1],"monetary":[100,80,20,5]})
    result=segment_customers(rfm)
    assert result["segment"].notna().all()
    assert set(result["segment"]).issubset({"Champions","Loyal Customers","At Risk","New Customers","Needs Attention"})
