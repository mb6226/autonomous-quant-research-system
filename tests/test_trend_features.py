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
    "ema20_above_50",
    "ema50_above_200",
    "ema20_above_200",
    "ema20_slope",
    "ema50_slope",
    "ema200_slope",
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
