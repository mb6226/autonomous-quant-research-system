import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf


class YahooProvider:

    def download_history(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "1d",
    ) -> pd.DataFrame:

        print(
            "START=",
            start_date,
            type(start_date),
        )

        print(
            "END=",
            end_date,
            type(end_date),
        )

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

        df = df.reset_index()

        if "Date" in df.columns:
            df = df.rename(
                columns={
                    "Date": "timestamp",
                }
            )

        if "Datetime" in df.columns:
            df = df.rename(
                columns={
                    "Datetime": "timestamp",
                }
            )

        df = df.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
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

    def download_history_chunked(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "1h",
    ) -> pd.DataFrame:

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        chunks = []

        if "h" in interval:
            chunk_delta = timedelta(days=30)
        elif "d" in interval:
            chunk_delta = timedelta(days=3650)
        else:
            chunk_delta = timedelta(days=30)

        while start < end:
            chunk_end = min(start + chunk_delta, end)

            print(
                "CHUNK:",
                start.strftime("%Y-%m-%d"),
                "->",
                chunk_end.strftime("%Y-%m-%d"),
            )

            df_chunk = yf.download(
                ticker,
                start=start.strftime("%Y-%m-%d"),
                end=chunk_end.strftime("%Y-%m-%d"),
                interval=interval,
                auto_adjust=False,
                progress=False,
            )

            if df_chunk.empty:
                start = chunk_end
                continue

            if isinstance(df_chunk.columns, pd.MultiIndex):
                df_chunk.columns = [col[0] for col in df_chunk.columns]

            df_chunk = df_chunk.reset_index()

            if "Date" in df_chunk.columns:
                df_chunk = df_chunk.rename(columns={"Date": "timestamp"})

            if "Datetime" in df_chunk.columns:
                df_chunk = df_chunk.rename(columns={"Datetime": "timestamp"})

            df_chunk = df_chunk.rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                }
            )

            cols = ["timestamp", "open", "high", "low", "close", "volume"]
            present = [c for c in cols if c in df_chunk.columns]
            df_chunk = df_chunk[present]

            chunks.append(df_chunk)

            start = chunk_end

        if not chunks:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

        df = pd.concat(chunks, ignore_index=True)

        if "timestamp" in df.columns:
            df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

        return df
