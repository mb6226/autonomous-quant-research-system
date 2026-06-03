# Google Colab Migration Plan — AQRS

Summary
- Objective: move heavy research workloads (W.F.V. benchmarks, ExperimentRunner, PromotionEngine) from local machine to Google Colab (Drive-backed) to reduce local CPU/RAM usage and enable reproducible remote runs.

Advantages
- Offloads CPU and RAM from local machine.
- Easy access to GPUs (if needed) and larger RAM on Pro tiers.
- Persistent storage via Google Drive.
- Simple developer onboarding — single notebook to reproduce environment.

Limitations
- Colab session timeouts (12 hours for Pro, variable for Free). Long runs may need checkpointing to Drive.
- Unreliable availability and preemption on free tiers.
- Colab compute is ephemeral; careful artifact writes to Drive required.

Expected speedup
- Dependent on Colab tier and local hardware. Typical speedup range:
  - Colab Free vs laptop CPU-only: 1.5–4x for CPU-bound training when using multi-core BLAS.
  - Colab Pro/Pro+: 2–8x depending on thread/BLAS configuration and RAM.

Cost comparison (very approximate)
- Colab Free: $0 — best for short experiments and prototyping.
- Colab Pro: ~$10–20/month — higher memory, faster GPUs, longer runtimes.
- Colab Pro+: ~$50/month — more vCPU/RAM, faster throughput for model grid runs.
- Google Cloud Compute (GCE): pay-per-hour, recommended when you need long, dedicated runs.

Checkpointing & orchestration
- Persist intermediate model artifacts, predictions and benchmark outputs to Drive under `/content/drive/MyDrive/aqrs_artifacts/`.
- Use periodic saves in scripts (e.g. ExperimentRunner to write intermediate results per-model to Drive).

Next steps
1. Prepare Colab notebook that mounts Drive, installs deps, sets `PYTHONPATH`, and verifies parquet access.
2. Create a small wrapper script `scripts/run_on_colab.sh` that can be launched from a Colab cell to run the benchmark scripts and write artifacts to Drive.
3. Validate with a short run (single timeframe, single model) to confirm environment and IO performance.
