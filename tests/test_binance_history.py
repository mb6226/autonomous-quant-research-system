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
    end_date="2026-06-01",
    provider="binance",
)

df = BinanceProvider().download_history(
    job
)

print(
    "ROWS =",
    len(df),
)

print(
    "FIRST =",
    df["timestamp"].min(),
)

print(
    "LAST =",
    df["timestamp"].max(),
)
