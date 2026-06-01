from app.data.jobs.download_job import (
    DownloadJob,
)

from app.research.universe_registry import (
    UNIVERSE,
    TIMEFRAMES,
)

def generate_jobs():

    jobs = []

    for symbol, provider in (
        UNIVERSE.items()
    ):

        for timeframe in TIMEFRAMES:

            jobs.append(
                DownloadJob(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date="2020-01-01",
                    end_date="2025-12-31",
                    provider=provider,
                )
            )

    return jobs
