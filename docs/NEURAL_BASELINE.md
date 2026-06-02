Neural Baseline: MLP Classifier
=================================

Overview
--------
This document records the MLP neural baseline introduced as a comparison point against tree-based models.

Model
-----
- `MLPClassifierModel` (sklearn)
- Defaults: `hidden_layer_sizes=(128,64)`, `activation='relu'`, `solver='adam'`, `max_iter=500`, `random_state=42`

Benchmarking
------------
- The model is included in the model family WFV benchmark and persisted to `artifacts/model_family_benchmark_wfv.json`.

Comparison
----------
- Compare average WFV accuracy against tree family (`xgboost`, `lightgbm`, `random_forest`, `extra_trees`, `catboost`).

Observations
------------
- Use this neural baseline to determine whether neural methods add value for this task; do not promote to production without additional validation.
