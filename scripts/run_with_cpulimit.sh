#!/usr/bin/env bash
# Simple wrapper that starts a command and attaches `cpulimit` to its PID.
# Usage: ./scripts/run_with_cpulimit.sh --limit 10 -- python run_pipeline.py

set -euo pipefail

LIMIT=10

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)
      LIMIT="$2"; shift 2;;
    --)
      shift; break;;
    *)
      break;;
  esac
done

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 --limit 10 -- <command...>"
  exit 2
fi

CMD=("$@")

if ! command -v cpulimit >/dev/null 2>&1; then
  echo "cpulimit not found. Install on Debian/Ubuntu: sudo apt-get install cpulimit"
  exit 1
fi

"${CMD[@]}" &
PID=$!
echo "Started PID $PID; applying cpulimit -l $LIMIT"
cpulimit -p $PID -l "$LIMIT" &
CPULIMIT_PID=$!

wait $PID

# cleanup
kill $CPULIMIT_PID 2>/dev/null || true
