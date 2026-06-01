from app.data_lake.dataset_store import (
    DatasetStore,
)

from app.data.validation.validator import (
    DatasetValidator,
)

df = DatasetStore().load(
    symbol="BTCUSDT",
    timeframe="1d",
)

errors = (
    DatasetValidator()
    .validate(df)
)

print(
    "ROWS =",
    len(df),
)

print(
    "ERRORS =",
    errors,
)
