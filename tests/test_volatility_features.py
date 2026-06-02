import pandas as pd

from app.features.feature_factory import (
    FeatureFactory,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1d.parquet"
)

df = (
    FeatureFactory()
    .build(df)
)

cols = [
    "volatility_5",
    "volatility_10",
    "volatility_20",
    "atr_ratio",
    "high_low_ratio",
]

print(
    df[cols].tail()
)

print()

for col in cols:
    print(
        col,
        col in df.columns,
    )
