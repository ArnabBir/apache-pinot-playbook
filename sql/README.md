# SQL and Query Examples

The files in this directory are grouped by engine and intent:

- [`01_smoke.sql`](sql/01_smoke.sql) and [`02_kpis_by_city.sql`](sql/02_kpis_by_city.sql) work with the single-stage `/query/sql` endpoint.
- [`04_multistage_join.sql`](sql/04_multistage_join.sql) and [`05_multistage_windows.sql`](sql/05_multistage_windows.sql) are written for the multi-stage `/query` endpoint.
- [`timeseries_gmv_request.json`](sql/timeseries_gmv_request.json) demonstrates the time-series broker-compatible API payload.
- [`07_upsert_debug.sql`](sql/07_upsert_debug.sql) and [`08_segment_pruning.sql`](sql/08_segment_pruning.sql) are diagnostic queries for operators.

A suggested workflow:

1. Run `python scripts/query_pinot.py --file sql/01_smoke.sql`
2. Run `python scripts/query_pinot.py --file sql/02_kpis_by_city.sql`
3. Run `python scripts/query_pinot.py --file sql/04_multistage_join.sql --query-type multistage`
