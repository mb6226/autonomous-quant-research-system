import pandas as pd
import yfinance as yf


class YahooProvider:

    def download_history(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "1d",
    ) -> pd.DataFrame:

        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            auto_adjust=False,
            progress=False,
        )

        if isinstance(
            df.columns,
            pd.MultiIndex,
        ):
            df.columns = [
                col[0]
                for col in df.columns
            ]

        df = (
            df.reset_index()
            .rename(
                columns={
                    "Date": "timestamp",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                }
            )
        )

        return df[
            [
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        ]
