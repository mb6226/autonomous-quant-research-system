import pandas as pd

from app.targets.target_factory import (
    TargetFactory,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1d.parquet"
)

target = (
    TargetFactory()
    .forward_return(
        df,
        periods=20,
    )
)

print(target.head())

print(
    "VALID =",
    target.notna().sum(),
)

print(
    "NAN =",
    target.isna().sum(),
)
