# AQRS V1 Final Report

## Executive Summary

AQRS (Autonomous Quant Research System) has reached V1 maturity: a reproducible, automated research platform capable of data collection, feature generation, experiment orchestration, validation, ranking, and governed promotion decisions. This report summarizes the system evolution, validation practices, governance, model timeline, and the production decision to adopt LightGBM as the production baseline.

---

## Research Automation Evolution

- Experiment Generator: automated experiment creation with permutations of features, targets, and model configs to explore large design spaces.
- Batch Research Runner: orchestrates batched experiment execution across datasets and timeframes to scale experiments without manual intervention.
- Auto Leaderboard: automatically aggregates experiment metrics, ranks models, and surfaces top candidates for follow-up.
- Auto Feature Selection: automated feature importance and selection pipelines that reduce dimensionality and serve as inputs to experiments.
- Multi Market Research Runner: runs the same experiments across multiple markets to assess cross-market generalization.
- Research Report Generator: compiles experiment artifacts, validation outputs, and promotion decisions into a human-readable research report.

These components were added incrementally to improve throughput, reproducibility, and decision traceability.

---

## Validation Evolution

- Single Split Validation: the original, simple validation used to get early feedback quickly. It exposed overfitting and temporal leakage risks in time-series data.
- Walk Forward Validation (WFV): introduced to respect temporal order and simulate rolling retraining and evaluation. WFV reduces optimistic bias from single-split validation and better estimates out-of-sample performance.
- Cross Market Validation: added to evaluate model generalization across instruments/markets. It prevents promotion of strategies that only work on a single market.
- Cross Market Stability Validation: stability-aware extension that runs WFV across multiple random seeds and markets, reporting mean and std of key metrics. It enforces a stability gate so that only candidates with sufficiently low variance are eligible for promotion.

Each step was added to address specific failure modes: single-split optimism, time-based drift, market-specific overfitting, and seed-driven instability.

---

## Governance Evolution

- Model Lifecycle Policy: formalized statuses (experimental, benchmark, production, archived) and clear promotion/demotion rules.
- Promotion Engine V1: initial automation that ranked candidates on mean metrics and produced promotion recommendations.
- Promotion Engine V2: enhanced to enforce governance rules, read stability artifacts, and block promotion of high-variance models.
- Stability Gate: a numeric rule (example: `std_accuracy <= 0.02`) requiring low variance across seeds/folds for production eligibility.
- Promotion Automation: end-to-end promotion artifacts are written (`promotion_decision.json`) and tracked for audit.

These governance additions ensure promotions are auditable, stable, and aligned with production reliability requirements.

---

## Model Evolution (chronological)

1. Random Forest
   - Benchmark result: solid baseline with moderate variance.
   - Governance result: eligible as a benchmark model; not chosen for production.
   - Current status: benchmark candidate.

2. XGBoost
   - Benchmark result: strong performance on many experiments.
   - Governance result: benchmark; considered for production depending on stability.
   - Current status: benchmark candidate.

3. LightGBM
   - Benchmark result: top-performing tree-based model in WFV and cross-market runs.
   - Governance result: passed walk-forward, cross-market, and stability validations.
   - Current status: Production model (see Section 6).

4. CatBoost
   - Benchmark result: competitive with other boosters on some markets.
   - Governance result: benchmark candidate; not promoted to production.
   - Current status: benchmark candidate.

5. Extra Trees
   - Benchmark result: occasionally high mean accuracy in sampled runs, higher variance observed.
   - Governance result: strong benchmark but lost top spot under stability averaging.
   - Current status: benchmark candidate.

6. MLP
   - Benchmark result: lower mean accuracy than tree ensembles in full-data runs.
   - Governance result: failed the stability gate (std_accuracy > threshold) and therefore disqualified for production.
   - Current status: rejected promotion candidate.

---

## Current Production Decision

Production Model: LightGBM

Reason:
- Passed Walk-Forward Validation
- Passed Cross-Market Validation
- Passed Cross-Market Stability Validation
- Lower variance than competitors in the cross-market stability runs

---

## Current Benchmark Set

- LightGBM
- Extra Trees
- CatBoost
- XGBoost
- Random Forest
- MLP

---

## Rejected Promotion Candidates

- MLP — rejected because `std_accuracy` exceeded the governance threshold in stability validation.

---

## Open Research Questions

- Can MLP stability be improved via architectural changes, regularization, or training protocol changes?
- Can Extra Trees outperform LightGBM after formal statistical significance testing across seeds/folds?
- Does feature scaling or normalization improve neural stability for MLPs?
- Are transformer models competitive (left as an open question for Phase 2)?

---

## AQRS V2 Roadmap (Phase 2)

Neural Sequence Models (exploratory):
- LSTM
- GRU
- Transformer

Prerequisite: any proposed neural/sequential model must demonstrably outperform the current LightGBM production baseline on walk-forward, cross-market, and stability validations before being considered for promotion.

---

## Appendix

Artifacts and metrics referenced in this report are persisted under `artifacts/` (e.g., cross-market validation, stability runs, and promotion decisions) for audit and reproducibility.
