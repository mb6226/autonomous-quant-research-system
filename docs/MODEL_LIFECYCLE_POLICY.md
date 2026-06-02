# Model Lifecycle Policy

Date: 2026-06-02

This document defines the lifecycle stages and governance rules for models in AQRS.

Lifecycle Stages

- Experimental: new models under active evaluation.
- Benchmark: models that are continuously evaluated across canonical benchmarks.
- Production: models allowed in automated research reports and production pipelines.
- Archived: models no longer actively benchmarked or deployed.

Movement Rules

- Experimental → Benchmark:
  - Must have a reproducible benchmark result on canonical datasets.
  - Must include documentation and a short review.
  - Requires peer review sign-off.

- Benchmark → Production:
  - Requires multiple benchmark cycles showing stable improvement.
  - Satisfy reproducibility and performance criteria.
  - Documentation and governance approval required.

- Production → Archived:
  - Triggered after multiple degraded benchmark cycles or clear evidence of sustained inferiority.
  - Archival requires documentation and approval.

Model Sets

- Benchmark Models: continuously evaluated to measure progress. They include models that provide performance or diversity value.
- Production Models: a smaller set used in reports and production to minimize maintenance overhead.
- Experimental Models: under trial; may be promoted or dropped.
- Archived Models: retained for record and offline exploration.

Current Classification (canonical baseline)

- Production:
  - xgboost

- Benchmark:
  - random_forest
  - extra_trees
  - lightgbm
  - catboost

- Experimental: (none)
- Archived: (none)

Governance Notes

- Benchmark sets and production sets are separate; a model can be in the benchmark set without being in production.
- Benchmarking must use `ExperimentRunner(allow_sampling=False)` and persist canonical results.
- Changes to model sets must be approved and recorded in documentation.
