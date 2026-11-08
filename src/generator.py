"""Deterministic synthetic CRM data generator for the YottaFlex challenge."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from .config import SEED, N_REPS, N_ACCOUNTS, N_OPPORTUNITIES, N_QUARTERS, DATA_DIR

STAGES = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
STAGE_PROB = {"Prospecting": .08, "Qualification": .20, "Proposal": .45,
              "Negotiation": .70, "Closed Won": 1.0, "Closed Lost": 0.0}
STAGE_NEXT = {"Prospecting": "Qualification", "Qualification": "Proposal",
              "Proposal": "Negotiation", "Negotiation": "Closed Won"}
PRODUCTS = ["Platform", "Analytics", "Automation", "AI Suite", "Integration"]
REGIONS = ["North", "South", "East", "West", "Central"]
INDUSTRIES = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Education"]
ACTIVITY_TYPES = ["Call", "Email", "Meeting", "Demo", "Proposal Sent"]
ISSUE_TYPES = ["forecast_uses_final_outcome", "stage_probability_mismatch",
               "duplicate_opportunity_counted", "close_date_before_creation", "mixed_currency_total"]

def _id(prefix: str, n: int, width: int = 6) -> str:
    return f"{prefix}-{n:0{width}d}"

def generate_dataset(output_dir: str | Path = DATA_DIR, seed: int = SEED,
                     n_reps: int = N_REPS, n_accounts: int = N_ACCOUNTS,
                     n_opportunities: int = N_OPPORTUNITIES,
                     n_quarters: int = N_QUARTERS) -> dict:
    """Generate normalized tables and a separate anomaly ground-truth file."""
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2024-01-01")
    quarter_ends = pd.date_range(start, periods=n_quarters, freq="QE")
    # Master data first: all child foreign keys are selected from these IDs.
    territories = pd.DataFrame([
        {"territory_id": f"TER-{i+1:03d}", "territory_name": f"{REGIONS[i]} Territory",
         "region": REGIONS[i], "effective_from": "2024-01-01",
         "effective_to": None if i != 4 else "2025-12-31"}
        for i in range(len(REGIONS))
    ])
    reps = pd.DataFrame({
        "rep_id": [_id("REP", i+1) for i in range(n_reps)],
        "rep_name": [f"Sales Rep {i+1:04d}" for i in range(n_reps)],
        "territory_id": rng.choice(territories.territory_id, n_reps),
        "hire_date": (start - pd.to_timedelta(rng.integers(0, 900, n_reps), unit="D")).strftime("%Y-%m-%d"),
        "active": True
    })
    accounts = pd.DataFrame({
        "account_id": [_id("ACC", i+1) for i in range(n_accounts)],
        "account_name": [f"Account {i+1:05d}" for i in range(n_accounts)],
        "territory_id": rng.choice(territories.territory_id, n_accounts),
        "industry": rng.choice(INDUSTRIES, n_accounts),
        "created_date": (start - pd.to_timedelta(rng.integers(0, 1200, n_accounts), unit="D")).strftime("%Y-%m-%d"),
        "annual_revenue": np.round(rng.lognormal(15.5, .8, n_accounts), 2)
    })
    stages = pd.DataFrame([{"stage_id": f"STG-{i+1:02d}", "stage_name": s,
                            "default_probability": STAGE_PROB[s], "stage_order": i+1}
                           for i, s in enumerate(STAGES)])
    # Opportunities
    created_offsets = rng.integers(0, 730, n_opportunities)
    created = start + pd.to_timedelta(created_offsets, unit="D")
    close_dates = created + pd.to_timedelta(rng.integers(20, 240, n_opportunities), unit="D")
    rep_idx = rng.integers(0, n_reps, n_opportunities)
    account_idx = rng.integers(0, n_accounts, n_opportunities)
    stage_choices = rng.choice(STAGES, n_opportunities, p=[.18,.24,.25,.16,.11,.06])
    amounts = np.round(rng.lognormal(10.3, .85, n_opportunities), 2)
    currencies = rng.choice(["USD", "USD", "USD", "EUR", "INR"], n_opportunities)
    opportunities = pd.DataFrame({
        "opportunity_id": [_id("OPP-2026", i+1) for i in range(n_opportunities)],
        "account_id": accounts.account_id.to_numpy()[account_idx],
        "rep_id": reps.rep_id.to_numpy()[rep_idx],
        "territory_id": accounts.territory_id.to_numpy()[account_idx],
        "stage_id": [stages.loc[stages.stage_name.eq(s), "stage_id"].iloc[0] for s in stage_choices],
        "stage": stage_choices,
        "amount": amounts,
        "currency": currencies,
        "product": rng.choice(PRODUCTS, n_opportunities),
        "created_date": created.strftime("%Y-%m-%d"),
        "close_date": close_dates.strftime("%Y-%m-%d"),
        "is_open": ~np.isin(stage_choices, ["Closed Won", "Closed Lost"]),
        "final_outcome": np.where(stage_choices == "Closed Won", "Won",
                           np.where(stage_choices == "Closed Lost", "Lost", "Pending"))
    })
    opportunities["opportunity_age_days"] = (pd.Timestamp("2026-10-31") - created).days
    # Stage history: creation event plus current stage event, with deterministic event IDs.
    hist_rows = []
    for i, row in opportunities.iterrows():
        hist_rows.append({"stage_history_id": f"STG-{row.opportunity_id}-001",
                          "opportunity_id": row.opportunity_id, "stage": "Prospecting",
                          "changed_at": row.created_date, "change_reason": "Opportunity created"})
        if row.stage != "Prospecting":
            hist_rows.append({"stage_history_id": f"STG-{row.opportunity_id}-002",
                              "opportunity_id": row.opportunity_id, "stage": row.stage,
                              "changed_at": row.created_date, "change_reason": "Synthetic stage progression"})
    stage_history = pd.DataFrame(hist_rows)
    # Activities linked to valid opportunity and rep.
    n_activities = n_opportunities * 2
    act_opp_idx = rng.integers(0, n_opportunities, n_activities)
    activity_dates = pd.to_datetime(opportunities.created_date.to_numpy()[act_opp_idx]) + pd.to_timedelta(
        rng.integers(0, 180, n_activities), unit="D")
    activities = pd.DataFrame({
        "activity_id": [_id("ACT", i+1, 8) for i in range(n_activities)],
        "opportunity_id": opportunities.opportunity_id.to_numpy()[act_opp_idx],
        "rep_id": opportunities.rep_id.to_numpy()[act_opp_idx],
        "activity_type": rng.choice(ACTIVITY_TYPES, n_activities),
        "activity_date": activity_dates.strftime("%Y-%m-%d"),
        "completed": rng.choice([True, False], n_activities, p=[.92,.08])
    })
    # Quotas by rep and quarter.
    quota_rows = []
    for q, qend in enumerate(quarter_ends):
        for rep in reps.itertuples():
            quota_rows.append({"quota_id": f"QUOTA-{rep.rep_id}-{qend.year}Q{qend.quarter}",
                               "rep_id": rep.rep_id, "quarter": f"{qend.year}Q{qend.quarter}",
                               "period_end": qend.strftime("%Y-%m-%d"),
                               "quota_amount": round(float(rng.uniform(90000, 220000)), 2),
                               "currency": "USD"})
    quotas = pd.DataFrame(quota_rows)
    # Ground-truth outcomes are derived from a documented probability model, not random labels.
    stage_index = {s:i for i,s in enumerate(STAGES)}
    win_probs = []
    for row in opportunities.itertuples():
        p = STAGE_PROB[row.stage]
        age_penalty = max(0, row.opportunity_age_days - 150) * .00035
        win_probs.append(float(np.clip(p - age_penalty, .01, .98)))
    outcomes = []
    for row, p in zip(opportunities.itertuples(), win_probs):
        if row.stage == "Closed Won": outcome = "Won"
        elif row.stage == "Closed Lost": outcome = "Lost"
        else:
            # Outcome deterministic from stable hash; reproducible and rule-based.
            h = int(hashlib.sha256(row.opportunity_id.encode()).hexdigest()[:8], 16) / 0xffffffff
            outcome = "Won" if h < p else "Lost"
        outcomes.append(outcome)
    opportunities["final_outcome"] = outcomes
    opportunities["is_open"] = opportunities.final_outcome.eq("Pending")
    bookings = opportunities.loc[opportunities.final_outcome.eq("Won"),
        ["opportunity_id","account_id","rep_id","territory_id","amount","currency","close_date"]].copy()
    bookings.insert(0, "booking_id", [f"BOOK-{i+1:07d}" for i in range(len(bookings))])
    bookings = bookings.rename(columns={"close_date":"booking_date","amount":"booking_amount"})
    # Snapshot per quarter: only data known at snapshot date; exclude later final outcomes from features.
    snap_frames = []
    activity_dates_dt = pd.to_datetime(activities.activity_date)
    activity_work = activities.assign(_activity_dt=activity_dates_dt)
    for qend in quarter_ends:
        eligible_mask = pd.to_datetime(opportunities.created_date) <= qend
        eligible = opportunities.loc[eligible_mask].copy()
        counts = (activity_work.loc[activity_work._activity_dt <= qend]
                  .groupby("opportunity_id").size())
        snap = pd.DataFrame({
            "snapshot_id": [f"FCST-{qend.strftime('%Y-%m-%d')}-{oid}" for oid in eligible.opportunity_id],
            "snapshot_date": qend.strftime("%Y-%m-%d"),
            "opportunity_id": eligible.opportunity_id.to_numpy(),
            "stage": eligible.stage.to_numpy(),
            "stage_probability": eligible.stage.map(STAGE_PROB).to_numpy(),
            "amount": eligible.amount.to_numpy(),
            "currency": eligible.currency.to_numpy(),
            "opportunity_age_days": (qend - pd.to_datetime(eligible.created_date)).dt.days.clip(lower=0).to_numpy(),
            "rep_id": eligible.rep_id.to_numpy(),
            "territory_id": eligible.territory_id.to_numpy(),
            "close_date": eligible.close_date.to_numpy(),
            "activity_count_to_date": eligible.opportunity_id.map(counts).fillna(0).astype(int).to_numpy()
        })
        snap_frames.append(snap)
    snapshots = pd.concat(snap_frames, ignore_index=True) if snap_frames else pd.DataFrame()
    # Historical booking rollups (quarterly, USD-equivalent illustrative conversion rates).
    fx = {"USD":1.0, "EUR":1.08, "INR":0.012}
    if len(bookings):
        bookings["amount_usd"] = bookings.apply(lambda r: r.booking_amount * fx[r.currency], axis=1)
        bookings["quarter"] = pd.to_datetime(bookings.booking_date).dt.to_period("Q").astype(str)
        hist_bookings = bookings.groupby("quarter", as_index=False).amount_usd.sum().rename(columns={"amount_usd":"bookings_usd"})
    else:
        hist_bookings = pd.DataFrame(columns=["quarter","bookings_usd"])
    # Deliberately labelled anomaly rows are isolated from the clean baseline tables.
    anomaly_rows = []
    chosen = opportunities.head(min(5, len(opportunities)))
    for i, (row, issue) in enumerate(zip(chosen.itertuples(), ISSUE_TYPES)):
        anomaly_rows.append({"issue_id": f"ISSUE-{i+1:03d}", "issue_type": issue,
            "entity_id": row.opportunity_id, "ground_truth_label": 1,
            "expected_detection": True,
            "description": [
                "A downstream forecast was computed from final outcome rather than snapshot-time state.",
                "Stored stage probability disagrees with the stage definition.",
                "The same opportunity is duplicated in a forecast aggregation.",
                "Close date precedes opportunity creation date.",
                "A total combines unconverted currencies."
            ][i]})
    ground_truth = pd.DataFrame(anomaly_rows)
    # Export all tables. Use stable row ordering and ISO dates.
    tables = {
        "sales_reps.csv": reps, "territories.csv": territories, "accounts.csv": accounts,
        "stages.csv": stages, "opportunities.csv": opportunities, "stage_history.csv": stage_history,
        "activities.csv": activities, "quotas.csv": quotas, "historical_bookings.csv": bookings,
        "historical_booking_rollup.csv": hist_bookings, "forecast_snapshots.csv": snapshots,
        "ground_truth.csv": ground_truth
    }
    for name, df in tables.items():
        df.to_csv(out / name, index=False)
    manifest = {"generator":"yottaflex-synthetic-crm-v1","seed":int(seed),
        "parameters":{"sales_reps":int(n_reps),"accounts":int(n_accounts),
                      "opportunities":int(n_opportunities),"quarters":int(n_quarters)},
        "currency_policy":"Forecast totals use USD conversion: USD=1.00, EUR=1.08, INR=0.012.",
        "outcome_policy":"Closed stages are fixed; open outcomes use a SHA256-derived uniform variate compared with stage probability adjusted for age.",
        "tables":{}}
    for name, df in tables.items():
        manifest["tables"][name] = {"rows":len(df),"sha256":hashlib.sha256((out/name).read_bytes()).hexdigest()}
    (out/"source_manifest.json").write_text(json.dumps(manifest, indent=2))
    return {"output_dir":str(out),"tables":{k:len(v) for k,v in tables.items()},"seed":seed}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output", default=str(DATA_DIR))
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--reps", type=int, default=N_REPS)
    p.add_argument("--accounts", type=int, default=N_ACCOUNTS)
    p.add_argument("--opportunities", type=int, default=N_OPPORTUNITIES)
    p.add_argument("--quarters", type=int, default=N_QUARTERS)
    a=p.parse_args()
    print(json.dumps(generate_dataset(a.output,a.seed,a.reps,a.accounts,a.opportunities,a.quarters),indent=2))
if __name__ == "__main__": main()
