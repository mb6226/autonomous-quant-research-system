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
    "roc_5",
    "roc_10",
    "roc_20",
    "ema20_distance",
    "ema50_distance",
    "ema200_distance",
    "rsi_momentum",
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
