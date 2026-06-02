# CatBoost Validation — Investigation Report

Date: 2026-06-02

Summary

- Standalone CatBoost run (direct script) produced:
  - TRAIN: 1859
  - TEST: 465
  - accuracy: 0.5053763440860215
  - precision: 0.512987012987013
  - recall: 0.33760683760683763
  - f1: 0.4072164948453608
  - confusion matrix: [[156, 75], [155, 79]]

- Benchmark run (tree models) produced for CatBoost:
  - SAMPLE_FRAC: 0.02
  - TRAIN: 21
  - TEST: 6
  - reported accuracy: 1.0
  - reported precision/recall/f1: 1.0

Root Cause Analysis

- The two runs used different sampling fractions. The benchmark was executed with `AQRS_SAMPLE_FRAC=0.02` active in the environment, producing a very small sample (TRAIN=21, TEST=6). The standalone test was executed without `AQRS_SAMPLE_FRAC` (default 1.0), using the full dataset (TRAIN=1859, TEST=465).
- The small sample in the benchmark makes results highly variable and allows perfect scores due to overfitting or class distribution quirks. Therefore the benchmark's CatBoost perfect score is not representative.
- Confirmed diagnostics: `tests/test_tree_model_benchmark.py` prints `SAMPLE_FRAC`, `TRAIN`, `TEST`, `y_train unique`, and `y_test unique`, and it saves `artifacts/benchmark_tree_models.json` for reproducibility.

Conclusion

- The discrepancy is caused by inconsistent sampling (environment variable) between standalone and benchmark runs. The benchmark is invalid for comparison until all models are evaluated on the same data splits and sample fractions.

Remediation and Recommendations

1. Re-run the benchmark with `AQRS_SAMPLE_FRAC=1.0` (or unset) to use the full dataset for fair comparison.
2. For development, prefix benchmark commands explicitly with `AQRS_SAMPLE_FRAC=...` to make sampling explicit in logs/scripts.
3. Persist benchmark outputs (`artifacts/benchmark_tree_models.json`) and include the `SAMPLE_FRAC` in the saved results (done by diagnostic script).
4. Consider adding an automated check that fails the benchmark when sample size is below a threshold (e.g., test_rows < 50).

Files and commands used

- Standalone CatBoost command (used):

```
PYTHONPATH=. OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 .venv/bin/python tests/test_catboost_classifier.py
```

- Benchmark command (used):

```
PYTHONPATH=. OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 .venv/bin/python tests/test_tree_model_benchmark.py
```

Audit artifacts

- artifacts/benchmark_tree_models.json (saved by benchmark script)
