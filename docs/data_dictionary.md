# Data Dictionary

| Entity / file | Primary key | Important fields | Relationship |
|---|---|---|---|
| sales_reps.csv | rep_id | name, territory, hire date, active | Rep belongs to territory |
| territories.csv | territory_id | name, region, effective dates | Parent of reps/accounts/opportunities |
| accounts.csv | account_id | name, territory, industry, revenue | Account belongs to territory |
| stages.csv | stage_id | stage name, default probability, order | Reference stage |
| opportunities.csv | opportunity_id | account, rep, stage, amount, currency, dates, outcome | Child of account/rep/stage |
| stage_history.csv | stage_history_id | opportunity, stage, changed_at | 1:N opportunity events |
| activities.csv | activity_id | opportunity, rep, type, date, completed | 1:N opportunity activities |
| quotas.csv | quota_id | rep, quarter, amount, currency | 1:N rep-quarter |
| historical_bookings.csv | booking_id | opportunity, amount, currency, date | 0:1 won opportunity |
| forecast_snapshots.csv | snapshot_id | snapshot date, stage, amount, age, activity count | 1:N opportunity snapshots |
| ground_truth.csv | issue_id | issue type, entity, expected detection | Separate labelled evaluation set |

All IDs are deterministic, immutable within a generated dataset, and zero-padded.
