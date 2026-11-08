# Forecasting and Validation Methodology

## Forecast
For opportunity i at snapshot t:

`ExpectedBookings_i,t = AmountUSD_i × StageProbability_i × AgeFactor_i × ActivityFactor_i × TimingFactor_i`

- Stage probabilities: Prospecting 8%, Qualification 20%, Proposal 45%, Negotiation 70%, Closed Won 100%, Closed Lost 0%.
- Age factor: 1.00 through 90 days, 0.92 for 91–180 days, 0.82 beyond 180 days.
- Activity factor: `clip(0.85 + 0.04 × min(completed + recorded activity count, 5), 0.85, 1.05)`.
- Timing factor: 1.00 if close date is within 90 days, 0.88 if later, 0.55 if close date is already past.
- Scenario multipliers: downside 0.80, base 1.00, upside 1.15.
- Slippage haircut applies to opportunities whose close date is more than 90 days after snapshot date.

## Leakage prevention
Snapshot inputs include stage, stage probability, amount, currency, age, activity count, close date, rep and territory as known on the snapshot date. Final outcome and ground-truth labels are excluded from `prepare_snapshot`.

## Evaluation
The `evaluate` function reports MAE, RMSE, MAPE and bias. For a production evaluation, use time-based holdouts, compare forecasts to realized bookings, and segment metrics by quarter, territory, stage and horizon.

## Exceptions
The challenge's five labelled anomaly types are represented in the isolated `ground_truth.csv`. The clean baseline tables remain internally consistent. Anomaly examples are labels for evaluation, not injected corruption of clean source tables.
