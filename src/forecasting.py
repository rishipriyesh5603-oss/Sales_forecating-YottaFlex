"""Snapshot-safe booking forecast and scenario simulation."""
from __future__ import annotations
import numpy as np
import pandas as pd

FX={"USD":1.0,"EUR":1.08,"INR":0.012}
STAGE_PROB={"Prospecting":.08,"Qualification":.20,"Proposal":.45,"Negotiation":.70,
            "Closed Won":1.0,"Closed Lost":0.0}

def prepare_snapshot(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Only snapshot-time fields are used. Outcome/ground_truth are intentionally excluded."""
    x=snapshot.copy()
    x["amount_usd"]=x.amount*x.currency.map(FX).fillna(1.0)
    x["age_bucket"]=pd.cut(x.opportunity_age_days,[-1,30,90,180,365,100000],
                           labels=["0-30","31-90","91-180","181-365","365+"])
    x["stage_probability"]=x.stage.map(STAGE_PROB)
    # Activity score is capped to avoid one noisy record dominating the forecast.
    x["activity_factor"]=np.clip(0.85 + .04*np.minimum(x.activity_count_to_date,5),.85,1.05)
    x["age_factor"]=np.where(x.opportunity_age_days>180,.82,
                      np.where(x.opportunity_age_days>90,.92,1.0))
    x["days_to_close"]=(pd.to_datetime(x.close_date)-pd.to_datetime(x.snapshot_date)).dt.days
    x["timing_factor"]=np.where(x.days_to_close<0,.55,np.where(x.days_to_close<=90,1.0,.88))
    x["forecast_probability"]=np.clip(x.stage_probability*x.activity_factor*x.age_factor*x.timing_factor,0,1)
    x["weighted_pipeline_usd"]=x.amount_usd*x.forecast_probability
    return x

def forecast(snapshot: pd.DataFrame, scenario: str="base", stage_uplift: float=0.0,
             slippage_rate: float=0.0) -> dict:
    if scenario not in {"downside","base","upside"}: raise ValueError("scenario must be downside, base, or upside")
    if not 0 <= slippage_rate <= 1: raise ValueError("slippage_rate must be in [0,1]")
    x=prepare_snapshot(snapshot)
    multiplier={"downside":.80,"base":1.0,"upside":1.15}[scenario]
    p=np.clip(x.forecast_probability*(1+stage_uplift)*multiplier,0,1)
    slipped=pd.to_datetime(x.close_date)>pd.to_datetime(x.snapshot_date)+pd.Timedelta(days=90)
    p=np.where(slipped,p*(1-slippage_rate),p)
    x["scenario_probability"]=p
    x["scenario_weighted_usd"]=x.amount_usd*p
    return {"scenario":scenario,"opportunity_count":int(len(x)),
            "gross_pipeline_usd":round(float(x.amount_usd.sum()),2),
            "weighted_bookings_usd":round(float(x.scenario_weighted_usd.sum()),2),
            "expected_wins":round(float(p.sum()),2),
            "slippage_rate":slippage_rate,"stage_uplift":stage_uplift,
            "by_stage":x.groupby("stage",observed=False).scenario_weighted_usd.sum().round(2).to_dict(),
            "by_territory":x.groupby("territory_id").scenario_weighted_usd.sum().round(2).to_dict(),
            "detail":x}

def evaluate(actual, predicted) -> dict:
    a=np.asarray(actual,dtype=float); p=np.asarray(predicted,dtype=float)
    if len(a)!=len(p) or not len(a): raise ValueError("actual and predicted must be non-empty and equal length")
    err=p-a
    denom=np.maximum(np.abs(a),1e-9)
    return {"mae":float(np.mean(np.abs(err))),"rmse":float(np.sqrt(np.mean(err**2))),
            "mape_pct":float(np.mean(np.abs(err)/denom)*100),"bias":float(np.mean(err))}

def scenario_comparison(snapshot: pd.DataFrame, slippage_rate: float=.15) -> pd.DataFrame:
    rows=[]
    for s in ["downside","base","upside"]:
        r=forecast(snapshot,s,slippage_rate=slippage_rate)
        rows.append({"scenario":s,"weighted_bookings_usd":r["weighted_bookings_usd"],
                     "expected_wins":r["expected_wins"],"gross_pipeline_usd":r["gross_pipeline_usd"]})
    return pd.DataFrame(rows)
