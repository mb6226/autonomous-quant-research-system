from app.data.providers.yahoo.provider import YahooProvider
from app.data_lake.dataset_store import DatasetStore
from app.data.manifests.manifest_store import ManifestStore
from app.data.validation.validator import DatasetValidator

df = YahooProvider().download_history(
    ticker="GC=F",
    start_date="2020-01-01",
    end_date="2026-06-01",
    interval="1d",
)

errors = DatasetValidator().validate(df)

print("ERRORS =", errors)
print("ROWS =", len(df))

DatasetStore().save(
    df=df,
    symbol="XAUUSD",
    timeframe="1d",
)

ManifestStore().save(
    name="XAUUSD_1d",
    payload={
        "symbol": "XAUUSD",
        "timeframe": "1d",
        "provider": "yahoo",
        "rows": len(df),
        "start": str(df["timestamp"].min()),
        "end": str(df["timestamp"].max()),
    },
)

print("DONE")
