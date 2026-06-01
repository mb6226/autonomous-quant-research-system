import pandas as pd

from app.research.dataset_builder import (
    ResearchDatasetBuilder,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1d.parquet"
)

dataset = (
    ResearchDatasetBuilder()
    .build(df)
)

print(
    dataset.columns.tolist()
)

print()

print(
    dataset.tail()
)

print()

print(
    "ROWS =",
    len(dataset),
)
