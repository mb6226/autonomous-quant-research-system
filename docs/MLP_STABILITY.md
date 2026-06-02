MLP Stability Validation
=========================

This document records the stability validation of the MLP baseline across multiple random seeds.

Artifact: `artifacts/mlp_stability.json`

Summary fields:
- `mean_accuracy`, `std_accuracy`
- `mean_precision`, `std_precision`
- `mean_recall`, `std_recall`
- `mean_f1`, `std_f1`
- `production_allowed`: boolean

Recommendation: If `std_accuracy > 0.02` the MLP should not be promoted to Production and should remain in Benchmark until stability improves.

Run the stability validator to regenerate the artifact and update this document.
