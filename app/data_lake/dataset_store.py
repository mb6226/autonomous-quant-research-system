from pathlib import Path

import pandas as pd

DATA_ROOT = Path(
    "data/raw"
)

class DatasetStore:

    def save(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str,
    ):

        directory = (
            DATA_ROOT / symbol
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            directory
            / f"{timeframe}.parquet"
        )

        df.to_parquet(
            path,
            index=False,
        )

    def load(
        self,
        symbol: str,
        timeframe: str,
    ):

        path = (
            DATA_ROOT
            / symbol
            / f"{timeframe}.parquet"
        )

        return pd.read_parquet(
            path
        )
