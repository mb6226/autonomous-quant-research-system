from app.data.factory.dataset_factory import (
    DatasetFactory,
)

dataset = (
    DatasetFactory()
    .create(
        symbol="BTCUSDT",
        timeframe="1h",
    )
)

print(dataset)
