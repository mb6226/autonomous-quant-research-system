# Monthly AI Pipeline Audit

Date: 2026-06-05

Summary
-------
- Pipeline run: completed successfully for all months (195 months).
- Progress file: `artifacts/monthly_ai_progress.json` — 195 completed, 0 failed, 100%.
- Per-month results: stored in `artifacts/monthly_ai_results/{YYYY-MM}.json` (195 files).

Automated per-month inspection (aggregate)
-----------------------------------------
- Rows processed (example): months range ~2k–33k rows (see per-file rows).
- Features created: `features_created` == 2 for every month.
- Targets created: `targets_created` == 1 for every month.
- `model_metrics` keys: `mean_close`, `std_close`, `rows` for months that contained a `close` column.
- No per-month JSON contains accuracy/AUC/F1 or explicit trained model metadata.

Detailed findings
-----------------
1) For every month file in `artifacts/monthly_ai_results/` the produced JSON contains only summary statistics (mean/std of `close`) and counts. Example keys: `mean_close`, `std_close`, `rows`.

2) The orchestrator script `scripts/eurusd_monthly_ai_pipeline.py` was inspected.
- It performs:
  - read parquet for month
  - sort by `timestamp`
  - compute two rolling features (`rmean_5`, `rstd_5`) when `close` is present
  - create a single target column `target_next_up` (binary)
  - write a small JSON with `rows`, `features_created`, `targets_created`, `model_metrics`
  - update checkpoint and logs

- It does NOT import or call any ML training libraries (no references to `lightgbm`, `catboost`, `xgboost`, `sklearn.ensemble`, `sklearn.neural_network.MLPClassifier`, or similar). The script does not implement a training loop, cross-validation, or any model fit/predict calls.

Questions answered
------------------
1. Did it actually call LightGBM? No.
2. CatBoost? No.
3. XGBoost? No.
4. RandomForest? No.
5. ExtraTrees? No.
6. MLP? No.
7. Did it call WalkForwardValidator? No.
8. Did it actually fit any model? No — no fit/training calls are present.
9. Did it only create metadata/checkpoints? Yes — the pipeline created features, targets, per-month statistics and checkpoint/JSON metadata only.

Estimated runtime if real training had occurred
----------------------------------------------
Estimate assumptions: average month ≈ 30k rows, small feature sets (< 20 features). Single-model single-fit times (very approximate):
- LightGBM / XGBoost / CatBoost: ~1–10 seconds per fit on 30k rows (single-threaded minimal params).
- RandomForest / ExtraTrees: ~10–60 seconds per fit (depends on n_estimators and trees depth).
- Small MLP (few layers): ~5–60 seconds depending on epochs and batch size.

If a rolling Walk-Forward validation with 5 windows were used, multiply fit time by ~5 (so LightGBM per-month with WFV ≈ 5–50s). For 195 months full run time estimate:
- LightGBM w/o WFV: 195 * 1–10s ≈ 3–33 minutes.
- LightGBM w/ 5-fold WFV: 195 * 5–50s ≈ 16–162 minutes (0.3–2.7 hours).
- RandomForest w/ WFV: likely multiple hours (≈ 1–6+ hours), depending on hyperparameters and parallelism.

Conclusions & recommendations
-----------------------------
- The pipeline did not perform model training — it produced deterministic metadata (rolling features and target) and summary statistics.
- If your intent was to train models per month (or run walk-forward validation), update `scripts/eurusd_monthly_ai_pipeline.py` to call the chosen trainer and record training/validation times and model info into the per-month JSON.
- Suggested minimal changes to enable training per-month:
  - add explicit imports and a `fit_and_validate()` function that returns model type, fit duration, validation duration and metrics.
  - record timestamps for `training_start`, `training_end`, `validation_start`, `validation_end` in the per-month JSON.
  - keep the pipeline resume-safe by writing results atomically and updating checkpoints after successful training.

Artifacts produced during this audit
----------------------------------
- `artifacts/_monthly_ai_audit_summary.json` — machine-readable summary of per-month rows/features/targets (created during this audit).
- `docs/MONTHLY_AI_PIPELINE_AUDIT.md` — this file.

If you want, I can now:
- implement a simple per-month trainer (LightGBM) and re-run only the months you choose, or
- modify the pipeline to support configurable trainers (LightGBM/CatBoost/XGBoost) and validation (walk-forward) with runtime estimates.

— Audit completed by assistant.
