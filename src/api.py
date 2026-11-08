from __future__ import annotations
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from .config import DATA_DIR
from .generator import generate_dataset
from .validation import validate_dataset
from .forecasting import forecast
from .analytics import build_summary

app=FastAPI(title="YottaFlex Sales Forecast API",version="1.0.0",
            description="Snapshot-safe sales pipeline forecasting and synthetic CRM data validation.")
def ensure_data():
    if not (DATA_DIR/"opportunities.csv").exists():
        generate_dataset(DATA_DIR)
ensure_data()

@app.get("/health")
def health(): return {"status":"ok","service":"yottaflex-sales-forecast"}

@app.get("/summary")
def summary():
    try: return build_summary(DATA_DIR)
    except Exception as e: raise HTTPException(500,str(e))

@app.get("/validate")
def validate():
    try: return validate_dataset(DATA_DIR)
    except Exception as e: raise HTTPException(422,str(e))

@app.get("/forecast")
def get_forecast(scenario: str=Query("base",pattern="^(downside|base|upside)$"),
                 slippage_rate: float=Query(.15,ge=0,le=1)):
    try:
        snap=pd.read_csv(DATA_DIR/"forecast_snapshots.csv")
        latest=snap[snap.snapshot_date==snap.snapshot_date.max()]
        result=forecast(latest,scenario,slippage_rate=slippage_rate)
        result.pop("detail",None)
        return result
    except Exception as e: raise HTTPException(422,str(e))

@app.get("/opportunities")
def opportunities(limit:int=Query(100,ge=1,le=1000),stage:str|None=None):
    df=pd.read_csv(DATA_DIR/"opportunities.csv")
    if stage: df=df[df.stage.eq(stage)]
    return df.head(limit).to_dict(orient="records")
