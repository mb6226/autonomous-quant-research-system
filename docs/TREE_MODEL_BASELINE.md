# AQRS Tree Model Baseline

Date: 2026-06-02

This document records the canonical benchmark for tree-based models on the BTCUSDT 1d dataset with target `classification_up_down_5`.

Model Ranking (by accuracy)


1. xgboost — accuracy 0.5634
2. random_forest — accuracy 0.5290
3. lightgbm — accuracy 0.5269
4. catboost — accuracy 0.5054
5. extra_trees — accuracy 0.4968

Metrics Table

| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| xgboost | 0.5634408602 | 0.6083916084 | 0.3717948718 | 0.4615384615 |
| random_forest | 0.5290322581 | 0.5510204082 | 0.3461538462 | 0.4251968504 |
| lightgbm | 0.5268817204 | 0.5333333333 | 0.4786324786 | 0.5045045045 |
| catboost | 0.5053763441 | 0.5129870130 | 0.3376068376 | 0.4072164948 |
| extra_trees | 0.4967741935 | 0.5 | 0.5384615385 | 0.5185185185 |

Best Model

- `xgboost` is the best-performing model on this baseline according to accuracy.

Observations

- Results were generated with `ExperimentRunner(allow_sampling=False)` to ensure full-dataset evaluation.
- `AQRS_SAMPLE_FRAC` is ignored for production benchmarks unless sampling is explicitly enabled.
- CatBoost's standalone metrics match the benchmark result after fixing sampling guards.
- No model reported `accuracy = 1.0` in the canonical benchmark; previous `1.0` was due to a tiny sampled run and is not reproducible.

Location of canonical results: `artifacts/tree_model_benchmark.json`

Walk-Forward Validation Baseline

The benchmark was re-run using `WalkForwardValidator` (4 folds, expanding training windows). Results were persisted to `artifacts/tree_model_benchmark_wfv.json`.

WFV Model Ranking (by average accuracy)

1. lightgbm — average accuracy 0.49364547876276454
2. catboost — average accuracy 0.4914671821814415
3. xgboost — average accuracy 0.4893212594346603
4. random_forest — average accuracy 0.473185215332248
5. extra_trees — average accuracy 0.4678157836317892

Comparison: Single Split vs Walk-Forward

- Single-split champion: `xgboost` (accuracy 0.56344) — measured on a single chronological split.
- Walk-forward champion: `lightgbm` (average accuracy 0.49365) — more robust across time windows.
- Rankings differ slightly; gaps are small. Walk-forward results should be preferred for stability-sensitive decisions.

Observations

- Some models (e.g., `xgboost`, `lightgbm`, `catboost`) are stable performers across both evaluations; others show variance.
- Use the Walk-Forward baseline for governance and promotion decisions.

