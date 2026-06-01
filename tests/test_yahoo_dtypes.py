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

print(df.dtypes)
