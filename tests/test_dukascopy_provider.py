from app.data.jobs.download_job import (
    DownloadJob,
)

from app.data.providers.dukascopy.provider import (
    DukascopyProvider,
)

job = DownloadJob(
    symbol="EURUSD",
    timeframe="1h",
    start_date="2020-01-01",
    end_date="2025-12-31",
    provider="dukascopy",
)

DukascopyProvider().download(
    job
)
