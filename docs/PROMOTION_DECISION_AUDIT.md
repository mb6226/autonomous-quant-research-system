Promotion Decision Audit
========================

Context
-------
The Promotion Engine was upgraded to V2 to include a stability gate: a candidate must have `std_accuracy <= 0.02` to be eligible for Production.

Inputs
------
- `artifacts/model_family_benchmark_wfv.json` (contains MLP as top by average_accuracy)
- `artifacts/mlp_stability.json` (stability results across seeds)

Previous Decision (V1)
----------------------
- V1 promoted the highest average_accuracy model.
- With the model-family WFV, that would have been: `mlp` (average_accuracy 0.49577).

New Decision (V2)
------------------
- Re-generated promotion decisions using V2 stability-aware rules.
- Final Production: `lightgbm`
- Benchmark set: `mlp`, `lightgbm`, `catboost`, `xgboost`, `random_forest`

Reason For Change
-----------------
- Although `mlp` had the highest average_accuracy (0.49577), the stability validation shows:

```
mean_accuracy = 0.49983
std_accuracy  = 0.03908
threshold     = 0.02000
production_allowed = false
```

- Because `std_accuracy` exceeds the stability threshold, `mlp` is not eligible for Production under V2.

Stability Gate Result
---------------------
- Source artifact: `artifacts/mlp_stability.json`
- `production_allowed`: false (std_accuracy 0.03908 > 0.02)

Audit Artifact
--------------
- Regenerated promotion decision: `artifacts/promotion_decision.json` (stability-aware)

Next Steps
----------
- Keep `mlp` in the Benchmark set and prioritize stability improvements (feature scaling, regularization, seed-averaging).
- Re-run the stability validator after remediation and re-evaluate promotion.
