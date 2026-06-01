from app.data.jobs.download_job import DownloadJob
from app.data.providers.binance.provider import BinanceProvider
from app.data.validation.validator import DatasetValidator
from app.data_lake.dataset_store import DatasetStore
from app.data.manifests.manifest_store import ManifestStore

job = DownloadJob(
    symbol="BTCUSDT",
    timeframe="4h",
    start_date="2020-01-01",
    end_date="2026-06-01",
    provider="binance",
)

df = BinanceProvider().download_history(job)

errors = DatasetValidator().validate(df)

print("ERRORS =", errors)

if errors:
    raise ValueError(errors)

DatasetStore().save(
    df=df,
    symbol="BTCUSDT",
    timeframe="4h",
)

ManifestStore().save(
    "BTCUSDT_4h",
    {
        "symbol": "BTCUSDT",
        "timeframe": "4h",
        "provider": "binance",
        "rows": len(df),
        "start": str(df["timestamp"].min()),
        "end": str(df["timestamp"].max()),
    },
)

print("DONE")
