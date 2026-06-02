# LSTM Baseline Specification

1. Objective

Why LSTM is being evaluated

- Evaluate a sequence-model baseline (LSTM) for time-series classification using the existing AQRS feature set. The goal is to establish a working neural baseline for Phase 2 before any integration with validation or promotion systems.

2. Input Data

Markets:
- BTCUSDT
- EURUSD
- XAUUSD
- USOIL
- US30

Timeframe:
- 1d

Target:
- `classification_up_down_5`

3. Sequence Construction

Sequence Length:
- 20

Input Shape:
- `(sequence_length, num_features)` where `num_features` is the number of features produced by the AQRS feature factory for the chosen dataset.

4. Model Architecture

LSTM

- `hidden_size = 64`
- `num_layers = 2`
- `dropout = 0.2`

Output:
- Binary classification logits for `classification_up_down_5` (use sigmoid/binary cross-entropy at training time).

5. Training Protocol

- `epochs = 20`
- `batch_size = 64`
- `learning_rate = 0.001`
- `optimizer = Adam`
- `loss = BCEWithLogitsLoss`

Notes:
- Use reproducible seeding for experiments.
- Apply standard training improvements (learning-rate scheduling, gradient clipping) as optional ablations.

6. Evaluation Plan

Phase 1: single market benchmark (create baseline on BTCUSDT 1d)

Phase 2: walk-forward validation (integrate WFV after stable baseline exists)

Phase 3: cross-market validation

Phase 4: cross-market stability validation (seeded runs)

Phase 5: promotion evaluation against governance rules

Important: For initial baseline (Phase 1) do not integrate WFV/cross-market/promotion — the goal is a working implementation and basic metrics.

7. Success Criteria

- Must outperform the LightGBM production baseline on the same dataset and target under the evaluation protocol (eventual WFV / cross-market comparisons). For Phase 1, success is establishing a working baseline with measurable metrics.

8. Risks

- Overfitting on small datasets
- Unstable training dynamics for neural nets
- Sensitivity to feature scaling and normalization
- High sensitivity to random seeds and initialization

9. Open Questions

- Optimal sequence length for different markets
- Best scaling/normalization strategy for features
- Appropriate hidden size and number of layers for generalization
