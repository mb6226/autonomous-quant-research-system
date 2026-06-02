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
    "bull_regime",
    "bear_regime",
    "high_vol_regime",
    "low_vol_regime",
    "trend_regime",
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
