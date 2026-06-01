from app.data.jobs.job_generator import (
    generate_jobs,
)

jobs = generate_jobs()

print(
    "TOTAL_JOBS =",
    len(jobs),
)

for job in jobs[:5]:
    print(job)
