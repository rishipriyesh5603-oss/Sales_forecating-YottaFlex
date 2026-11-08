from __future__ import annotations
import pandas as pd
from .forecasting import forecast, scenario_comparison

def build_summary(data_dir):
    from pathlib import Path
    d=Path(data_dir)
    opp=pd.read_csv(d/"opportunities.csv")
    snap=pd.read_csv(d/"forecast_snapshots.csv")
    latest=snap[snap.snapshot_date==snap.snapshot_date.max()]
    base=forecast(latest,"base",slippage_rate=.15)
    return {"opportunities":len(opp),"open_opportunities":int(opp.is_open.sum()),
            "closed_won":int(opp.final_outcome.eq("Won").sum()),
            "closed_lost":int(opp.final_outcome.eq("Lost").sum()),
            "gross_pipeline_usd":base["gross_pipeline_usd"],
            "weighted_forecast_usd":base["weighted_bookings_usd"],
            "scenarios":scenario_comparison(latest).to_dict(orient="records"),
            "by_stage":base["by_stage"],"by_territory":base["by_territory"]}
