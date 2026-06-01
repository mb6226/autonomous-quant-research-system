import pandas as pd

from datetime import datetime, timedelta, UTC

from app.data.providers.yahoo.provider import (
    YahooProvider,
)

from app.data.providers.yahoo.symbol_mapper import (
    YAHOO_SYMBOLS,
)

from app.data.validation.validator import (
    DatasetValidator,
)

from app.data_lake.dataset_store import (
    DatasetStore,
)

from app.data.manifests.manifest_store import (
    ManifestStore,
)

end_date = datetime.now(UTC)
start_date = end_date - timedelta(days=729)

df = YahooProvider().download_history(
    ticker=YAHOO_SYMBOLS["US30"],
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d"),
    interval="1h",
)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True,
)

errors = (
    DatasetValidator()
    .validate(df)
)

print("ERRORS =", errors)

if errors:
    raise ValueError(errors)

DatasetStore().save(
    df=df,
    symbol="US30",
    timeframe="1h",
)

ManifestStore().save(
    "US30_1h",
    {
        "symbol": "US30",
        "timeframe": "1h",
        "provider": "yahoo",
        "rows": len(df),
        "start": str(
            df["timestamp"].min()
        ),
        "end": str(
            df["timestamp"].max()
        ),
    },
)

print("ROWS =", len(df))
print("DONE")
from app.data.providers.yahoo.provider import (
    YahooProvider,
)

from app.data.providers.yahoo.symbol_mapper import (
    YAHOO_SYMBOLS,
)

from app.data.validation.validator import (
    DatasetValidator,
)

from app.data_lake.dataset_store import (
    DatasetStore,
)

from app.data.manifests.manifest_store import (
    ManifestStore,
)

df = YahooProvider().download_history(
    ticker=YAHOO_SYMBOLS["EURUSD"],
    start_date="2020-01-01",
    end_date="2026-06-01",
)

errors = (
    DatasetValidator()
    .validate(df)
)

print("ERRORS =", errors)

if errors:
    raise ValueError(errors)

DatasetStore().save(
    df=df,
    symbol="EURUSD",
    timeframe="1d",
)

ManifestStore().save(
    "EURUSD_1d",
    {
        "symbol": "EURUSD",
        "timeframe": "1d",
        "provider": "yahoo",
        "rows": len(df),
        "start": str(
            df["timestamp"].min()
        ),
        "end": str(
            df["timestamp"].max()
        ),
    },
)

print("ROWS =", len(df))
print("DONE")
