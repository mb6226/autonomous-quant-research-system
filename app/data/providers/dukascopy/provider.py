from app.data.jobs.download_job import (
    DownloadJob,
)

class DukascopyProvider:

    def download(
        self,
        job: DownloadJob,
    ):

        print(
            "DOWNLOADING",
            job.symbol,
            job.timeframe,
        )
