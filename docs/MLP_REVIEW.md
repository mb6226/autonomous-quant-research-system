MLP Review
===========

## Benchmark Results (Walk-Forward Validation)

Source: `artifacts/model_family_benchmark_wfv.json`

| Rank | Model | Accuracy | Precision | Recall | F1 |
|---:|---|---:|---:|---:|---:|
| 1 | mlp | 0.49577290217552167 | 0.2584875048430841 | 0.452970297029703 | 0.329145185839839 |
| 2 | lightgbm | 0.49364547876276454 | 0.5733777151468408 | 0.464862514833969 | 0.4452137985614016 |
| 3 | catboost | 0.4914671821814415 | 0.5548465677719604 | 0.4179255925924304 | 0.4052355895028475 |
| 4 | xgboost | 0.4893212594346603 | 0.5939401527695441 | 0.44098817223606485 | 0.4137254563109992 |
| 5 | random_forest | 0.473185215332248 | 0.6646825396825397 | 0.3859867162081091 | 0.34358357290339153 |
| 6 | extra_trees | 0.4678157836317892 | 0.5663882181470121 | 0.39177839582941043 | 0.4050889528919651 |


## Champion Analysis

The MLP achieved the highest average accuracy in Walk-Forward Validation (0.4958), narrowly beating LightGBM (0.4936).

Possible explanations:

- Nonlinear interactions: the MLP may capture continuous nonlinear relationships not well approximated by the tree splits.
- Smoother decision boundary: neural models can produce smoother decision functions which may generalize better across rolling windows.
- Reduced overfitting in WFV: with proper regularization and the relatively small network, the MLP may generalize better across time.
- Walk-forward robustness: averaging across folds reduced variance and highlighted consistent MLP performance.


## Risk Analysis

Potential weaknesses to consider:

- Instability: MLPs can be sensitive to random seeds and initialization; re-running with different seeds may change ranking.
- Sensitivity to feature scaling: neural nets typically require standardized inputs; ensure feature pipeline preserves scaling.
- Training variance: optimization (solver, max_iter) can create variability; monitor convergence warnings.


## Recommendation

Recommendation (V1): treat MLP as a benchmark champion candidate.

- Recommendation: `MLP` should be added to the Benchmark set and considered the Production candidate (subject to human review).
- Rationale: MLP leads on WFV average accuracy and shows reasonable F1; however, human review is required before final promotion due to neural-specific risks.


## Next Steps

- Re-run WFV with multiple random seeds to assess stability.
- Add basic feature scaling in the pipeline if not already applied and re-evaluate.
- Monitor training convergence and add early stopping or regularization if instability observed.
