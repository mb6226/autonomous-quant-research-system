#!/usr/bin/env bash
set -euo pipefail

# Run AQRS benchmark components from within Google Colab (or any mounted Drive).
# Usage (in Colab):
# %bash
# /content/drive/MyDrive/autonomous-quant-research-system/scripts/run_on_colab.sh /content/drive/MyDrive/autonomous-quant-research-system

REPO_DIR=${1:-/content/drive/MyDrive/autonomous-quant-research-system}
ARTIFACTS_DIR="$REPO_DIR/artifacts"
LOG_DIR="$ARTIFACTS_DIR/logs"
mkdir -p "$ARTIFACTS_DIR" "$LOG_DIR"

echo "Using REPO_DIR=$REPO_DIR"
export PYTHONPATH="$REPO_DIR":$PYTHONPATH

cd "$REPO_DIR"

echo "Installing Python requirements (may take a few minutes)"
pip install -r requirements.txt

# DO NOT start any data acquisition downloads from Colab. Ensure data/raw/* is populated in Drive.

echo "Running benchmark (dry-run option recommended first)"
# Example to run a single short benchmark: adjust TIMEFRAME/MODELS in the script to limit scope.
python scripts/eurusd_benchmark_wfv.py > "$LOG_DIR/eurusd_benchmark_wfv.out" 2>&1 || {
  echo "Benchmark script failed; check $LOG_DIR/eurusd_benchmark_wfv.out" >&2
  exit 1
}

echo "Benchmark finished; artifacts available in $ARTIFACTS_DIR"
