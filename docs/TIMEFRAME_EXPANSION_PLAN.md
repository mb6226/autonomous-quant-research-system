# Timeframe Expansion Plan

Objective: increase dataset size by adding higher-frequency intraday timeframes (30m, 15m, 5m) for existing markets before adding new markets.

Current Timeframes (from manifests):
- 1h, 4h, 1d (present for BTCUSDT, EURUSD, XAUUSD, USOIL, US30)

Missing Timeframes:
- 1m, 5m, 15m, 30m are currently missing for existing markets.

Expected Row Multipliers (relative to `1h` rows):
- 30m ≈ 2× 1h rows
- 15m ≈ 4× 1h rows
- 5m  ≈ 12× 1h rows

Rationale: intraday sampling increases row counts proportionally to the number of intervals per hour; these multipliers assume continuous coverage similar to existing 1h data.
