from datetime import datetime

import pandas as pd
import requests

from app.data.jobs.download_job import (
    DownloadJob,
)


class BinanceProvider:

    BASE_URL = (
        "https://api.binance.com/api/v3/klines"
    )

    def download(
        self,
        job: DownloadJob,
    ):

        interval_map = {
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
        }

        interval = interval_map[
            job.timeframe
        ]

        response = requests.get(
            self.BASE_URL,
            params={
                "symbol": job.symbol,
                "interval": interval,
                "limit": 1000,
            },
            timeout=30,
        )

        response.raise_for_status()

        rows = response.json()

        df = pd.DataFrame(
            rows,
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

        return df
