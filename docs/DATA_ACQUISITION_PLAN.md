# Data Acquisition Plan

Objective: convert the timeframe expansion roadmap into an executable acquisition plan to increase dataset size prior to any model complexity increases.

SECTION A — Current Dataset Size

- Current total rows (selected markets): 127,972
- Current markets: BTCUSDT, EURUSD, XAUUSD, USOIL, US30
- Current timeframes: 1h, 4h, 1d (per manifests)

SECTION B — Target Dataset Size

Projected totals if intraday timeframes are added across existing markets:

- After adding 30m: ~317,146 rows (≈ ×2.5)
- After adding 15m: ~506,320 rows (≈ ×4.0)
- After adding 5m:  ~1,263,016 rows (≈ ×9.9)

Expected growth factor: 30m ≈2.5×, 15m ≈4×, 5m ≈10× (relative to current total).

SECTION C — Acquisition Priority

Priority 1 (immediate): backfill intraday timeframes for existing markets:
- BTCUSDT, EURUSD, XAUUSD, USOIL, US30 — add 30m, 15m, 5m (30m easiest/cheapest).

Priority 2: expand depth for markets with low coverage (US30).

Priority 3: add new forex majors (GBPUSD, USDJPY, AUDUSD, etc.) and metals/commodities.

Priority 4: add US equities (see `docs/US_STOCK_EXPANSION.md` for feasibility notes).

SECTION D — Provider Sources (summary)

- Crypto: Binance (free API, rate-limited), Coinbase, Kraken. Commercial: Kaiko, CryptoCompare, CoinAPI (paid, higher fidelity).
- Forex: Dukascopy (historical tick), TrueFX, Oanda. Commercial providers offer more reliable tick/intraday history.
- Indices: Yahoo/AlphaVantage for daily; Polygon/Quandl for intraday (paid).
- Commodities: Exchange-provided feeds or brokers, Polygon/Quandl for paid intraday.

Considerations: free APIs are suitable for prototyping but have rate limits and possible missing history; paid providers improve coverage and reliability at cost.

SECTION E — Storage Projection (assumptions)

- Assumption: per-row parquet storage (compressed) ≈ 200 bytes (conservative estimate depending on feature count and compression).
- Current (127,972 rows) ≈ 25 MB
- After 30m (317,146 rows) ≈ 63 MB
- After 15m (506,320 rows) ≈ 101 MB
- After 5m (1,263,016 rows) ≈ 252 MB

SECTION F — Training Projection (assumptions)

- Training time and feature generation scale roughly linearly with number of rows.
- If current training (WFV) takes T, expect:
  - 30m: ≈ 2.5× T
  - 15m: ≈ 4× T
  - 5m:  ≈ 10× T
- Walk-forward runs will require proportionally more compute and storage for intermediate artifacts.

SECTION G — Recommended Next Actions

1. Acquire 30m data for BTCUSDT and EURUSD (low cost, high impact).
2. Validate ingestion and storage pipeline with 30m data.
3. Measure feature generation and training runtime; then scale to 15m where justified.
