Governance Audit
================

Promotion Engine Version
------------------------
- Promotion Engine V2 (stability-aware)

Current Production Model
------------------------
- lightgbm

Current Benchmark Models
------------------------
- mlp
- lightgbm
- catboost
- xgboost
- random_forest
- extra_trees

Current Stability Gate
----------------------
- `std_accuracy` must be <= 0.02 to be eligible for Production
- Seeds used for stability validation: [42, 123, 456, 789, 999]

Current Promotion Rules (summary)
---------------------------------
- Production: highest-ranked validated model by `average_accuracy` that also passes the stability gate (or has an artifact override permitting production).
- If top-ranked model fails stability, the next highest that passes is promoted.
- Benchmark: top-K models by `average_accuracy` (K=5 by default), irrespective of stability.
- Experimental: models missing validation folds or accuracy.
- Archived: validated models outside the benchmark.

Known Risks
-----------
- Stability artifacts and promotion decisions are stored under `artifacts/`. If artifacts are stale or missing, decisions may be inconsistent.
- `promotion_decision.json` may contain `eligible_for_production: false` without `std_accuracy` populated if an external artifact override was applied; always check `{model}_stability.json` for canonical stability numbers.
- New model families must not be added until stability remediation is complete and governance audits pass.
