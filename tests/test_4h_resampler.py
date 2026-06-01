from app.data.providers.yahoo.provider import (
    YahooProvider,
)

from app.data.providers.yahoo.symbol_mapper import (
    YAHOO_SYMBOLS,
)

from app.data.resampling.ohlc_resampler import (
    OHLCResampler,
)

df_1h = (
    YahooProvider()
    .download_history(
        ticker=YAHOO_SYMBOLS["EURUSD"],
        start_date="2025-01-01",
        end_date="2025-06-01",
        interval="1h",
    )
)

df_4h = (
    OHLCResampler()
    .to_4h(df_1h)
)

print(
    "1H ROWS =",
    len(df_1h),
)

print(
    "4H ROWS =",
    len(df_4h),
)

print(
    df_4h.head()
)
