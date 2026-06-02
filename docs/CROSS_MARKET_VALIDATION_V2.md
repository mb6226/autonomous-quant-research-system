Cross Market Validation V2 — Full Data
=====================================

Purpose
-------
Rerun cross-market validation using full datasets (no sampling) to confirm or refute the previous sampled result that made `extra_trees` the champion.

Previous Result
---------------
- Source artifact: `artifacts/cross_market_ranking.json` (sampled run)
- Reported champion: `extra_trees`
- Audit found: sampled run used `allow_sampling=True`, `sample_frac=0.2`; result INVALID.

V2 Run (this audit)
--------------------
- Run configuration: `CrossMarketValidator(allow_sampling=False)` — full datasets only.
- Markets evaluated: BTCUSDT, EURUSD, XAUUSD, USOIL, US30
- Models evaluated: lightgbm, mlp, catboost, xgboost, random_forest, extra_trees
- Validator: `WalkForwardValidator` (4 folds per market)

New Result (artifacts)
----------------------
- Artifact: `artifacts/cross_market_validation.json`
- Ranking: `artifacts/cross_market_ranking.json`

Champion
--------
- `extra_trees` (overall_average_accuracy = 0.54345)

Per-model overall accuracies
----------------------------
- extra_trees: 0.54345
- lightgbm: 0.52972
- catboost: 0.52929
- random_forest: 0.52578
- mlp: 0.51564
- xgboost: 0.50697

Margins
-------
- extra_trees vs lightgbm: +0.01373 (≈1.37 percentage points)
- extra_trees vs mlp: +0.02781 (≈2.78 percentage points)

Consistency Checks
------------------
- `allow_sampling`: explicitly set to `False` for this run — sampling not used.
- `AQRS_SAMPLE_FRAC`: ignored (not applied because `allow_sampling=False`).
- All models evaluated on the same markets — each per-market entry contains `folds: 4`.
- WalkForwardValidator used for all models (4 folds per market confirmed).

Statistical Considerations
--------------------------
- Inter-market variability remains large; the margin vs LightGBM (~1.37pp) is small relative to per-market differences (some markets show 3–4pp swings favoring different models).
- No seed-averaging/stability runs were performed in this cross-market V2 run; results are single WFV averages per market. For production decisions, perform stability validator runs per model to obtain std_accuracy and confidence intervals.

Conclusion
----------
- Although `extra_trees` remains the top-ranked model on full data by overall_average_accuracy, the margin vs `lightgbm` is small and not yet proven statistically robust.

Recommendation
--------------
- To validate promotion decisions, run stability-aware cross-market comparisons (seed averaging) and paired statistical tests across folds/markets. Only after stability and significance are confirmed should governance consider changing Production.
