import pandas as pd

from app.targets.target_factory import (
    TargetFactory,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1d.parquet"
)

target = (
    TargetFactory()
    .volatility(
        df,
        periods=5,
    )
)

print(target.head(10))

print(
    "VALID =",
    target.notna().sum(),
)

print(
    "NAN =",
    target.isna().sum(),
)
