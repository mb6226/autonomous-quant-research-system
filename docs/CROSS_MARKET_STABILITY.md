Cross-Market Stability Validation
================================

Purpose
-------
Run seed-averaged cross-market Walk-Forward Validation for champion candidates to assess stability.

Seeds
-----
42, 123, 456, 789, 999

Models evaluated
----------------
- extra_trees
- lightgbm
- mlp

Markets
-------
BTCUSDT, EURUSD, XAUUSD, USOIL, US30

Artifact
--------
`artifacts/cross_market_stability.json` (seed results, mean and std per model)

Key Results (mean_accuracy / std_accuracy)
-----------------------------------------
- extra_trees: mean_accuracy = 0.5105896310555862, std_accuracy = 0.005037262866401753
- lightgbm:   mean_accuracy = 0.5157014724232363, std_accuracy = 0.003956615651663845
- mlp:        mean_accuracy = 0.49615235344952396, std_accuracy = 0.020796574178160037

Interpretation
--------------
- After seed-averaging across the five specified seeds, `lightgbm` has the highest mean accuracy (0.51570) and the lowest std (0.00396).
- `extra_trees` is stable (std ≈ 0.00504) but has lower mean accuracy than `lightgbm` by ~0.00511 (0.51 vs 0.5157).
- `mlp` shows higher variability (std ≈ 0.02080) and fails the governance stability gate (std > 0.02), so it's not production-eligible without remediation.

Answer: Does Extra Trees remain champion after stability adjustment?
---------------------------------------------------------------
- No. After stability averaging across seeds, `lightgbm` has a higher mean accuracy than `extra_trees`. `extra_trees` is stable but not the top mean performer.

Recommendation
--------------
1. Given these stability results, prefer `lightgbm` as the cross-market champion subject to governance checks (stability gate passed and mean higher).
2. Run a paired statistical test across seeds/folds to confirm significance of the mean difference before any promotion action.
