from app.data_lake.dataset_store import (
    DatasetStore,
)

df = DatasetStore().load(
    symbol="BTCUSDT",
    timeframe="1d",
)

print(df.dtypes)

print()

print(df.head())
