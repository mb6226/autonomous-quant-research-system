# Research Reproducibility Rules

This document specifies rules for reproducible research runs in AQRS.

Run types

- Full Run: uses the entire dataset. Default for production, benchmarks, leaderboards, feature ranking, and reports.
- Sample Run: uses a sample fraction for development and quick debugging. Must be explicit and opt-in.

Rules

1. `AQRS_SAMPLE_FRAC` is respected only when `ExperimentRunner(allow_sampling=True)` is used.
2. Benchmarks, leaderboards, feature selection, and report generation must instantiate `ExperimentRunner(allow_sampling=False)` explicitly.
3. Tests that validate sampling behavior should set `AQRS_SAMPLE_FRAC` and exercise both `allow_sampling=True` and `False` to confirm behavior.
4. Production research artifacts must be generated with Full Run and marked accordingly in reports.

Example

```
# Full benchmark (recommended)
PYTHONPATH=. .venv/bin/python tests/test_tree_model_benchmark.py

# Sampled local run (explicit opt-in)
AQRS_SAMPLE_FRAC=0.02 PYTHONPATH=. .venv/bin/python -c "from app.research.experiment_runner import ExperimentRunner; ExperimentRunner(allow_sampling=True).run(...)"
```
