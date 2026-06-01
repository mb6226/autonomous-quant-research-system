import pandas as pd

from app.features.feature_factory import (
    FeatureFactory,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1h.parquet"
)

df = FeatureFactory().build(df)

print(
    df[
        [
            "close",
            "volume",
            "vwap",
        ]
    ].tail()
)

print(
    "VWAP EXISTS =",
    "vwap" in df.columns,
)
