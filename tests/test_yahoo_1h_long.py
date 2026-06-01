from app.data.providers.yahoo.provider import (
    YahooProvider,
)

from app.data.providers.yahoo.symbol_mapper import (
    YAHOO_SYMBOLS,
)

df = YahooProvider().download_history(
    ticker=YAHOO_SYMBOLS["EURUSD"],
    start_date="2020-01-01",
    end_date="2026-06-01",
    interval="1h",
)

print("ROWS =", len(df))

print(
    df["timestamp"].min()
)

print(
    df["timestamp"].max()
)
