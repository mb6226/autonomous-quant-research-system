from app.data.providers.yahoo.provider import (
    YahooProvider,
)

from app.data.providers.yahoo.symbol_mapper import (
    YAHOO_SYMBOLS,
)

ticker = YAHOO_SYMBOLS["EURUSD"]

df = YahooProvider().download_history(
    ticker=ticker,
    start_date="2020-01-01",
    end_date="2026-06-01",
    interval="1d",
)

print(df.head())

print()

print("ROWS =", len(df))

print(
    "FIRST =",
    df.iloc[0]["Date"],
)

print(
    "LAST =",
    df.iloc[-1]["Date"],
)
