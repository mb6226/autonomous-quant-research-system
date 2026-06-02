# Tree Family Review

Date: 2026-06-02

This review uses the canonical benchmark results saved in `artifacts/tree_model_benchmark.json` (BTCUSDT 1d, target `classification_up_down_5`).

## Model Ranking

1. xgboost
2. random_forest
3. lightgbm
4. catboost
5. extra_trees

## Metrics Table

| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| xgboost | 0.563441 | 0.608392 | 0.371795 | 0.461538 |
| random_forest | 0.529032 | 0.551020 | 0.346154 | 0.425197 |
| lightgbm | 0.526882 | 0.533333 | 0.478632 | 0.504505 |
| catboost | 0.505376 | 0.512987 | 0.337607 | 0.407216 |
| extra_trees | 0.496774 | 0.500000 | 0.538462 | 0.518519 |

## Champion

- `xgboost` is the current champion by accuracy (0.563441).

## Analysis

- Extra Trees vs Random Forest:
  - Accuracy gap: 0.529032 (RF) vs 0.496774 (ET) → ET is ~0.0323 lower in accuracy.
  - Extra Trees shows higher recall (0.538) and F1 (0.519) on this task, indicating it predicts the positive class more often at the cost of precision.
  - Net: Extra Trees does not outperform Random Forest on accuracy, but provides a complementary operating point (higher recall / F1).

- Extra Trees vs LightGBM:
  - LightGBM has higher accuracy (0.526882) and higher precision (0.533) while ET has higher recall (0.538).
  - ET does not outperform LightGBM overall by the accuracy metric.

- Extra Trees vs XGBoost:
  - XGBoost outperforms ET by ~0.0667 in accuracy and by precision/f1. ET does not compete with XGBoost on this benchmark.

- How large is the gap?
  - The largest accuracy gap is between XGBoost and Extra Trees (~0.0667). Between RF and ET the gap is modest (~0.0323).

## Recommendation

Apply the decision rules: keep a model only if it offers a measurable performance advantage or a diversity advantage.

- xgboost: KEEP — champion by accuracy.
- lightgbm: KEEP — close performance to RF and offers implementation diversity among boosting libraries.
- random_forest: KEEP — strong baseline and diversity vs boosting methods.
- catboost: KEEP — offers algorithmic diversity in boosting implementations and performs reasonably; keep for further evaluation.
- extra_trees: DROP from the active benchmark set — does not improve accuracy and is largely redundant with Random Forest. It can be retained offline for exploratory work but should not consume regular benchmark time.

## Active Tree Benchmark Set

- xgboost
- random_forest
- lightgbm
- catboost

Extra Trees: removed from the active benchmark set (recommendation: archived/optional).

## Notes

- These recommendations are based on a single canonical benchmark (BTCUSDT 1d). Consider cross-market validation and walk-forward tests before making long-term decisions.
