# US Stock Expansion Feasibility

This note outlines feasibility and considerations for expanding AQRS to include US equities.

Data source options

- Yahoo Finance: free, easy access, but limited historical depth and corporate actions handling.
- Alpha Vantage / IEX / Tiingo: APIs with varying rate limits and coverage; may require API keys and paid tiers for bulk historical data.
- Polygon / Intrinio / Quandl: commercial providers with higher-quality tick and minute-level data; suitable for production-grade datasets.

Adjusted OHLCV requirements

- For equities, ensure fields: `open, high, low, close, volume` and optionally `adj_close`.
- Use `adj_close` or adjust OHLC and volume for splits and dividends before computing returns.

Split handling

- Detect corporate actions (splits) and apply multiplicative adjustments to past prices and volumes.
- Maintain an `adjustments` table in dataset metadata for reproducibility.

Dividend handling

- Dividends affect total return — decide whether to use `adjusted close` (total return) or raw close plus explicit dividend series.
- For classification tasks over short horizons, `adjusted close` is usually sufficient.

Expected dataset scale

- US equities universe: thousands of tickers. For a focused baseline, start with top market-cap tickers (S&P 500 ~500 symbols).
- Daily timeframe: modest disk/compute (hundreds of MBs). Minute-level or tick data: large (GBs to TBs) and requires careful storage/ingestion planning.

Operational notes

- Ensure timezone normalization (US markets use Eastern Time; convert to UTC for consistency).
- Trading calendars: handle non-trading days/holidays when aligning cross-market experiments.
