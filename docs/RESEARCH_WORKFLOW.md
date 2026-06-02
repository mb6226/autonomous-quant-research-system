# Research Workflow (AQRS)

This document describes the automated research workflow for AQRS.

Pipeline

1. Experiment Generator
2. Experiment Runner
3. Multi Market Runner
4. Auto Leaderboard
5. Feature Selector
6. Report Generator

Example command (run from repository root):

```bash
PYTHONPATH=. python run_research.py
```

Notes

- Use `AQRS_SAMPLE_FRAC` only for quick local benchmarking. Production runs should not set this variable.
- Use Google Colab or a proper compute environment for full runs.
