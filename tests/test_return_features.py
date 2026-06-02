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

print(
    df[
        [
            "return_1",
            "return_5",
            "return_10",
            "return_20",
        ]
    ].tail()
)
