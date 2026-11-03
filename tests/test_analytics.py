import pandas as pd
from ecommerce_intel.analytics import monthly_revenue, build_rfm, cohort_retention
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
    assert row["monetary"]==30
    assert row["recency_days"]==2

def test_segmentation_adds_labels():
    rfm=pd.DataFrame({"customer_id":["a","b","c","d"],"recency_days":[1,10,20,30],"frequency":[10,8,2,1],"monetary":[100,80,20,5]})
    result=segment_customers(rfm)
    assert result["segment"].notna().all()
    assert set(result["segment"]).issubset({"Champions","Loyal Customers","At Risk","New Customers","Needs Attention"})

def test_cohort_retention_tracks_repeat_customers():
    df = transactions()
    df["is_valid_sale"] = True
    df["line_revenue"] = df.quantity * df.unit_price
    result = cohort_retention(df)
    jan = result.loc[result["cohort_month"] == pd.Timestamp("2011-01-01")].sort_values("cohort_index")
    assert jan["cohort_size"].iloc[0] == 2
    assert jan.loc[jan["cohort_index"] == 1, "retention_rate"].iloc[0] == 1.0
    assert jan.loc[jan["cohort_index"] == 2, "customers"].iloc[0] == 1
    assert jan.loc[jan["cohort_index"] == 2, "retention_rate"].iloc[0] == 0.5
