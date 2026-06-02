Run on Colab
============

This folder contains a Google Colab notebook and helper script to run parts of this repository on Google Colab.

Files:
- `Run_on_Colab.ipynb` - step-by-step Colab notebook for mounting Drive, cloning the repo, installing dependencies, configuring parallelism, and running tasks.
- `run_command.py` - small launcher used by the notebook to run commands with `PYTHONPATH` set to `/content/repo`.

Quick start (on Colab):
1. Open `tools/colab/Run_on_Colab.ipynb` in Google Colab.
2. Run the cells in order. Edit the background execution cell to run whichever command you need, e.g.:

```bash
nohup python -u /content/repo/tools/colab/run_command.py --cmd "python -m pytest -q tests/test_feature_selector.py -q" > /content/drive/MyDrive/aqrs-results/feature_selector.log 2>&1 &
```

3. Monitor logs in `/content/drive/MyDrive/aqrs-results/`.

Notes:
- Before running heavy CPU-bound jobs, set environment variables to limit threads (example in the notebook sets `OMP_NUM_THREADS=2`).
- Colab sessions may disconnect; save checkpoints and intermediate results to Drive.
- If you need GPU-accelerated XGBoost/LightGBM, uncomment and install GPU-specific wheels in the notebook.

Safety: Prevent accidental local execution
---------------------------------------
To avoid running heavy AI/CPU-bound processing on your laptop by mistake, use the `colab_launcher.py` script included in this folder. By default it refuses to run unless it detects a Google Colab environment. Example:

```bash
# safe launch (refuses to run on non-Colab unless you pass --allow-local)
python /content/repo/tools/colab/colab_launcher.py --cmd "python -u /content/repo/tools/colab/run_command.py --cmd 'python -m pytest -q tests/test_feature_selector.py -q'"
```

If you must force a local run (not recommended), add `--allow-local`.
