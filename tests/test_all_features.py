from pathlib import Path

import pandas as pd

from app.features.feature_factory import (
    FeatureFactory,
)

files = sorted(
    Path("data/raw").rglob("*.parquet")
)

print("DATASETS =", len(files))

for file in files:

    print()
    print(file)

    df = pd.read_parquet(file)

    df = FeatureFactory().build(df)

    required = [
        "ema20",
        "ema50",
        "ema200",
        "rsi14",
        "atr14",
    ]

    for col in required:
        assert col in df.columns, col

    print(
        "ROWS =",
        len(df),
    )

    print(
        "FEATURES OK",
    )

print()
print("ALL DATASETS PASSED")
