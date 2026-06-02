#!/usr/bin/env bash
# Run a command under a systemd scope limited to 10% CPU by default.
# Usage: ./scripts/run_with_cpuquota.sh --unit my-unit --quota 10% -- <command...>

set -euo pipefail

UNIT="aqrs-limited"
QUOTA="10%"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --unit)
      UNIT="$2"; shift 2;;
    --quota)
      QUOTA="$2"; shift 2;;
    --)
      shift; break;;
    *)
      break;;
  esac
done

if [[ $# -eq 0 ]]; then
  echo "No command provided. Example: $0 --quota 10% -- python run_pipeline.py"
  exit 2
fi

CMD="$*"

echo "Running under systemd scope unit=$UNIT CPUQuota=$QUOTA: $CMD"
systemd-run --scope -p CPUQuota=${QUOTA} --unit=${UNIT} bash -c "${CMD}"
