# YottaFlex AI — Sales Booking Forecasting Platform

A reproducible synthetic CRM data platform and scenario-based booking forecast for the YottaFlex 72-hour candidate challenge.

## What is included
- Deterministic synthetic data generator (seed `20261022`).
- Normalized CRM entities: SalesRep, Territory, Account, Opportunity, Stage, StageHistory, Activity, Quota, HistoricalBooking and ForecastSnapshot.
- 2,000 reps, 2,000 accounts, 20,000 opportunities and eight quarterly snapshots by default.
- Separate `ground_truth.csv` for labelled anomaly cases; never used as model input.
- Relational, date, enum, uniqueness and probability validation.
- Snapshot-safe booking forecast with downside/base/upside scenarios.
- FastAPI endpoints and Streamlit dashboard.
- Pytest tests, data dictionary, methodology and prompt history.

## Quick start (Python 3.11 or 3.12 recommended)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```
The generator writes CSV files to `data/` and validates them. For a quick small run:
```bash
python run.py --reps 30 --accounts 40 --opportunities 250 --quarters 4
```
To restore the challenge-sized dataset, run `python run.py` with no overrides.

## Start the dashboard
```bash
streamlit run frontend/app.py
```
## Start the API
```bash
uvicorn src.api:app --reload
```
Open `http://127.0.0.1:8000/docs` for interactive API documentation.

## API
- `GET /health`
- `GET /summary`
- `GET /validate`
- `GET /forecast?scenario=base&slippage_rate=0.15`
- `GET /opportunities?limit=100&stage=Proposal`

## Forecast method
At each snapshot, expected bookings are computed from snapshot-time amount, stage, opportunity age, activity count, close-date timing and currency conversion. The model never reads `final_outcome` or `ground_truth` as a forecast feature. Scenario multipliers are downside 0.80, base 1.00 and upside 1.15. A configurable slippage haircut is applied to opportunities closing more than 90 days after the snapshot.

The initial model is deliberately transparent and deterministic. It is a baseline suitable for synthetic data; production calibration should estimate conversion probabilities from real historical snapshot/outcome pairs and validate by time-based holdout.

## Data integrity and reproducibility
- Stable zero-padded IDs and explicit foreign keys.
- Master tables are generated before dependent tables.
- Fixed seed controls synthetic generation.
- SHA-256 checksums and row counts are written to `data/source_manifest.json`.
- `ground_truth.csv` is a separate labelled evaluation artifact.
- Re-run `python run.py` with the same parameters and seed to regenerate identical files.

## Known assumptions / limitations
- Currency conversion rates are illustrative, not live FX rates.
- Synthetic stage transitions and activities are generated to provide realistic test coverage, not to represent a real company's CRM.
- Historical snapshots are a synthetic baseline; production evaluation should use time-based splits and report MAE, RMSE, MAPE and bias by horizon and segment.
- A simple rule-based baseline is used instead of claiming a trained ML model where no real labelled training history exists.

## Repository checklist
1. Commit the source, docs and generated sample data.
2. Keep secrets, tokens and personal data out of Git.
3. Verify the repository is public in a private/incognito browser.
4. Submit the repository URL through the candidate portal.
