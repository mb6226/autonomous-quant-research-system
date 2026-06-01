from datetime import datetime, timedelta, UTC

from app.data.providers.yahoo.provider import YahooProvider
from app.data.providers.yahoo.symbol_mapper import YAHOO_SYMBOLS

end_date = datetime.now(UTC)
start_date = end_date - timedelta(days=729)

for symbol in [
    "EURUSD",
    "XAUUSD",
    "USOIL",
    "US30",
]:
    print("\n", symbol)

    df = YahooProvider().download_history(
        ticker=YAHOO_SYMBOLS[symbol],
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        interval="1h",
    )

    print("ROWS =", len(df))

    if len(df):
        print("FIRST =", df.iloc[0]["timestamp"])
        print("LAST =", df.iloc[-1]["timestamp"])
