from app.data_lake.dataset_store import (
    DatasetStore,
)

from app.features.feature_factory import (
    FeatureFactory,
)

df = DatasetStore().load(
    symbol="BTCUSDT",
    timeframe="1d",
)

features = (
    FeatureFactory()
    .build(df)
)

print(
    features[
        [
            "timestamp",
            "close",
            "return_1",
            "ema20",
            "ema50",
            "ema200",
            "rsi14",
            "atr14",
        ]
    ].tail()
)

print()

print(
    "ROWS =",
    len(features),
)

print(
    "COLUMNS =",
    len(features.columns),
)
