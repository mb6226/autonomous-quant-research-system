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
)

print(df.head())

print()
print(df.columns.tolist())

print()
print("ROWS =", len(df))
print("FIRST =", df.iloc[0]["timestamp"])
print("LAST =", df.iloc[-1]["timestamp"])
