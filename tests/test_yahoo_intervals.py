from app.data.providers.yahoo.provider import (
    YahooProvider,
)

from app.data.providers.yahoo.symbol_mapper import (
    YAHOO_SYMBOLS,
)

for tf in ["1h", "1d"]:

    try:

        df = YahooProvider().download_history(
            ticker=YAHOO_SYMBOLS["EURUSD"],
            start_date="2025-01-01",
            end_date="2025-06-01",
            interval=tf,
        )

        print(
            tf,
            len(df),
        )

    except Exception as e:

        print(
            tf,
            e,
        )
