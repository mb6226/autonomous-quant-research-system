Short guide: limiting CPU usage for project runs

Recommended (systemd scope)

- Use the included script to run any project command with a CPU quota:

  ./scripts/run_with_cpuquota.sh --quota 10% -- python run_pipeline.py

- The script calls `systemd-run --scope -p CPUQuota=...` and will limit all child processes created by the command.

Fallback / single-process

- For single-process runs, `cpulimit` can be used:

  sudo apt-get install cpulimit
  cpulimit -l 10 -- python run_pipeline.py

Thread-limiting (reduce BLAS threads)

Set these env vars before running to limit internal thread parallelism:

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

Notes

- `systemd-run` requires systemd; typical on modern Linux. `CPUQuota=10%` limits CPU usage relative to a single CPU.
- The wrapper is a convenience; you can also open an interactive limited shell with `systemd-run --scope -p CPUQuota=10% bash`.
