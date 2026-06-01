from app.data.jobs.download_job import (
    DownloadJob,
)

from app.data.providers.binance.provider import (
    BinanceProvider,
)

job = DownloadJob(
    symbol="BTCUSDT",
    timeframe="1d",
    start_date="2020-01-01",
    end_date="2025-12-31",
    provider="binance",
)

df = BinanceProvider().download(
    job
)

print(df.head())

print()

print(
    "ROWS =",
    len(df),
)
