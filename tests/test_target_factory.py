import pandas as pd

from app.targets.target_factory import (
    TargetFactory,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1d.parquet"
)

factory = TargetFactory()

target = factory.forward_return(
    df,
    periods=5,
)

print(target.tail())

print(
    "ROWS =",
    len(target),
)
