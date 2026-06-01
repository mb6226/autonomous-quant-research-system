from app.data.factory.provider_factory import (
    create_provider,
)

from app.data.jobs.job_generator import (
    generate_jobs,
)

class DownloadManager:

    def run(self):

        jobs = generate_jobs()

        for job in jobs:

            provider = (
                create_provider(
                    job.provider
                )
            )

            provider.download(
                job
            )
