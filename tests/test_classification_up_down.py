import pandas as pd

from app.targets.target_factory import (
    TargetFactory,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1d.parquet"
)

target = (
    TargetFactory()
    .classification_up_down(
        df,
        periods=1,
    )
)

print(
    target.head(10)
)

print()

print(
    "UP =",
    (target == 1).sum(),
)

print(
    "DOWN =",
    (target == 0).sum(),
)

print(
    "ROWS =",
    len(target),
)
