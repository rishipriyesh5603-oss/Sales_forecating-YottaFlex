from pathlib import Path
import pandas as pd
from src.generator import generate_dataset
from src.validation import validate_dataset
from src.forecasting import forecast, evaluate

def test_small_generation_and_validation(tmp_path):
    generate_dataset(tmp_path,seed=20261022,n_reps=12,n_accounts=15,n_opportunities=80,n_quarters=3)
    result=validate_dataset(tmp_path)
    assert result["passed"]
    assert len(pd.read_csv(tmp_path/"opportunities.csv"))==80

def test_forecast_is_snapshot_based():
    df=pd.DataFrame([{"snapshot_date":"2026-09-30","opportunity_id":"OPP-1",
        "stage":"Proposal","stage_probability":.45,"amount":10000,"currency":"USD",
        "opportunity_age_days":45,"rep_id":"REP-1","territory_id":"TER-001",
        "close_date":"2026-10-30","activity_count_to_date":3}])
    r=forecast(df,"base")
    assert r["weighted_bookings_usd"]>0
    assert "detail" in r

def test_metrics():
    m=evaluate([100,200],[110,190])
    assert round(m["mae"],2)==10
    assert m["rmse"]>0
