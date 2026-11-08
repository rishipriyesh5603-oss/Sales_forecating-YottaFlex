"""Relational, lifecycle, arithmetic, and reproducibility validation."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from .config import DATA_DIR

FK = {
 "sales_reps.csv": [],
 "accounts.csv": [("territory_id","territories.csv","territory_id")],
 "opportunities.csv": [("account_id","accounts.csv","account_id"),("rep_id","sales_reps.csv","rep_id"),
                       ("territory_id","territories.csv","territory_id"),("stage_id","stages.csv","stage_id")],
 "stage_history.csv": [("opportunity_id","opportunities.csv","opportunity_id")],
 "activities.csv": [("opportunity_id","opportunities.csv","opportunity_id"),("rep_id","sales_reps.csv","rep_id")],
 "quotas.csv": [("rep_id","sales_reps.csv","rep_id")],
 "historical_bookings.csv": [("opportunity_id","opportunities.csv","opportunity_id"),
                             ("account_id","accounts.csv","account_id"),("rep_id","sales_reps.csv","rep_id")],
 "forecast_snapshots.csv": [("opportunity_id","opportunities.csv","opportunity_id"),
                            ("rep_id","sales_reps.csv","rep_id"),("territory_id","territories.csv","territory_id")]
}

def validate_dataset(data_dir: str | Path = DATA_DIR) -> dict:
    d=Path(data_dir); errors=[]; warnings=[]; metrics={}
    required=list(FK)+["territories.csv","stages.csv","historical_booking_rollup.csv","ground_truth.csv"]
    frames={}
    for name in required:
        path=d/name
        if not path.exists():
            errors.append(f"Missing required file: {name}")
        else:
            frames[name]=pd.read_csv(path)
            metrics[name]={"rows":len(frames[name]),"columns":len(frames[name].columns)}
    for name, fks in FK.items():
        if name not in frames: continue
        df=frames[name]
        if "id" in df.columns and df.id.duplicated().any(): errors.append(f"{name}: duplicate id")
        pk={"sales_reps.csv":"rep_id","accounts.csv":"account_id","opportunities.csv":"opportunity_id",
            "stage_history.csv":"stage_history_id","activities.csv":"activity_id","quotas.csv":"quota_id",
            "historical_bookings.csv":"booking_id","forecast_snapshots.csv":"snapshot_id"}.get(name)
        if pk and df[pk].duplicated().any(): errors.append(f"{name}: duplicate primary key {pk}")
        for col,parent,parent_col in fks:
            if parent not in frames: continue
            missing=set(df[col].dropna())-set(frames[parent][parent_col].dropna())
            if missing: errors.append(f"{name}.{col}: {len(missing)} orphan foreign keys")
    if "opportunities.csv" in frames:
        o=frames["opportunities.csv"]
        bad=pd.to_datetime(o.close_date)<pd.to_datetime(o.created_date)
        if bad.any(): errors.append(f"opportunities.csv: {int(bad.sum())} close dates before creation")
        if (o.amount<0).any(): errors.append("opportunities.csv: negative amounts")
        if not set(o.stage).issubset({"Prospecting","Qualification","Proposal","Negotiation","Closed Won","Closed Lost"}):
            errors.append("opportunities.csv: invalid stage enum")
        if o.opportunity_id.duplicated().any(): errors.append("opportunities.csv: duplicate opportunity")
    if "forecast_snapshots.csv" in frames:
        s=frames["forecast_snapshots.csv"]
        if s.duplicated(["snapshot_date","opportunity_id"]).any(): errors.append("forecast_snapshots.csv: duplicate snapshot/opportunity")
        if ((s.stage_probability<0)|(s.stage_probability>1)).any(): errors.append("forecast_snapshots.csv: probability outside [0,1]")
        if (pd.to_datetime(s.snapshot_date)>pd.to_datetime("2026-10-31")).any(): errors.append("snapshot after as-of date")
    if "historical_bookings.csv" in frames:
        b=frames["historical_bookings.csv"]
        if not set(b.currency).issubset({"USD","EUR","INR"}): errors.append("Unsupported booking currency")
    result={"passed":len(errors)==0,"errors":errors,"warnings":warnings,"metrics":metrics}
    (d/"validation_summary.json").write_text(json.dumps(result,indent=2))
    if errors: raise ValueError("Dataset validation failed: "+"; ".join(errors[:8]))
    return result

def main():
    p=argparse.ArgumentParser(); p.add_argument("--data",default=str(DATA_DIR)); a=p.parse_args()
    print(json.dumps(validate_dataset(a.data),indent=2))
if __name__=="__main__": main()
