# Walk Forward Validation

Date: 2026-06-02

Why Walk-Forward?

For time-series model evaluation, a single train/test split can be misleading due to non-stationarity and temporal leakage. Walk-forward (rolling) validation evaluates models across multiple expanding windows, providing a more robust estimate of performance and stability over time.

How it works (example)

- Window 1: Train 0%→60%, Test 60%→70%
- Window 2: Train 0%→70%, Test 70%→80%
- Window 3: Train 0%→80%, Test 80%→90%
- Window 4: Train 0%→90%, Test 90%→100%

Use `WalkForwardValidator` (app/research/walk_forward_validator.py) to compute per-fold metrics and averages. For production benchmarks, always use `ExperimentRunner(allow_sampling=False)` and persist results.
