from app.data_lake.dataset_store import DatasetStore
from app.data.resampling.ohlc_resampler import OHLCResampler
from app.data.manifests.manifest_store import ManifestStore
from app.data.validation.validator import DatasetValidator

df_1h = DatasetStore().load(
    symbol="XAUUSD",
    timeframe="1h",
)

df_4h = OHLCResampler().to_4h(df_1h)

errors = DatasetValidator().validate(
    df_4h
)

print("ERRORS =", errors)
print("ROWS =", len(df_4h))

if errors:
    raise ValueError(errors)

DatasetStore().save(
    df=df_4h,
    symbol="XAUUSD",
    timeframe="4h",
)

ManifestStore().save(
    name="XAUUSD_4h",
    payload={
        "symbol": "XAUUSD",
        "timeframe": "4h",
        "provider": "yahoo_resampled",
        "rows": len(df_4h),
        "start": str(df_4h["timestamp"].min()),
        "end": str(df_4h["timestamp"].max()),
    },
)

print("XAUUSD 4h ->", len(df_4h))
