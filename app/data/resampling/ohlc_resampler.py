import pandas as pd


class OHLCResampler:

    @staticmethod
    def to_4h(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        df["timestamp"] = pd.to_datetime(
            df["timestamp"]
        )

        df = df.set_index(
            "timestamp"
        )

        resampled = (
            df
            .resample("4h")
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
            .dropna()
            .reset_index()
        )

        return resampled
