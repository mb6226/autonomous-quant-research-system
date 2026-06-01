import pandas as pd

from app.data_lake.dataset_store import (
    DatasetStore,
)

df = pd.DataFrame(
    {
        "timestamp": [
            "2025-01-01"
        ],
        "close": [
            100000
        ],
    }
)

store = DatasetStore()

store.save(
    df=df,
    symbol="BTCUSDT",
    timeframe="1h",
)

loaded = store.load(
    symbol="BTCUSDT",
    timeframe="1h",
)

print(loaded)
