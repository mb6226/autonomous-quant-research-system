# Data Coverage

This document summarizes available datasets, timeframes, row counts and coverage gaps discovered by `app/data/data_inventory.py`.

Available datasets (from manifests):

```
$(python -m app.data.data_inventory)
```

Summary (generated):

Largest datasets

- See `artifacts/data_coverage_report.json` for full details.

Smallest datasets

- See `artifacts/data_coverage_report.json` for full details.

Missing timeframes

- For each market, compare existing timeframes in `data/manifests` with desired intraday set (1m,5m,15m,30m,1h,4h,1d). Missing entries indicate candidates for data expansion.

Coverage gaps

- Fields `missing_values` in the report (if non-zero) indicate gaps inferred from start/end dates versus row counts.

Priority

- Expand intraday timeframes for existing markets before adding new markets.

See `artifacts/data_coverage_report.json` for the generated inventory.
