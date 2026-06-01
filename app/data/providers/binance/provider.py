import pandas as pd
import requests

from app.data.jobs.download_job import (
    DownloadJob,
)

from app.data.providers.binance.pagination import (
    to_milliseconds,
)


class BinanceProvider:

    BASE_URL = (
        "https://api.binance.com/api/v3/klines"
    )

    def download(
        self,
        job: DownloadJob,
    ):
        return self.download_history(
            job
        )

    def download_history(
        self,
        job: DownloadJob,
    ) -> pd.DataFrame:

        interval_map = {
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
        }

        interval = interval_map[
            job.timeframe
        ]

        start_time = (
            to_milliseconds(
                job.start_date
            )
        )

        end_time = (
            to_milliseconds(
                job.end_date
            )
        )

        all_rows = []

        while start_time < end_time:

            response = requests.get(
                self.BASE_URL,
                params={
                    "symbol": job.symbol,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": 1000,
                },
                timeout=30,
            )

            response.raise_for_status()

            rows = response.json()

            if not rows:
                break

            all_rows.extend(
                rows
            )

            start_time = (
                rows[-1][0] + 1
            )

            print(
                "DOWNLOADED",
                len(all_rows),
            )

        df = pd.DataFrame(
            all_rows,
            columns=[
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_volume",
                "trades",
                "tb_base",
                "tb_quote",
                "ignore",
            ],
        )

        df["timestamp"] = pd.to_datetime(
            df["open_time"],
            unit="ms",
            utc=True,
        )

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_volume",
            "tb_base",
            "tb_quote",
        ]

        for col in numeric_columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )

        df["trades"] = pd.to_numeric(
            df["trades"],
            errors="coerce",
        ).astype("int64")

        return df