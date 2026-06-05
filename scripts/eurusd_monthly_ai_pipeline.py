#!/usr/bin/env python3
"""Monthly AI training orchestrator for EURUSD 1m monthly files.

Processes files in data/raw/EURUSD/1m_monthly/*.parquet sequentially,
one month at a time. Records progress in artifacts/monthly_ai_progress.json
and per-month results in artifacts/monthly_ai_results/{month}.json.

CPU throttling: if `cpulimit` is available the script re-executes itself
under `cpulimit -l 10 -- <python> ...`. Otherwise the process niceness
is raised via `os.nice(19)`.

The script saves a PID to /tmp/monthly_ai.pid and logs to
logs/monthly_ai_pipeline.log.
"""
import os
import sys
import time
import json
import shutil
import gc
import argparse
from datetime import datetime, timezone

try:
    import pandas as pd
except Exception:
    print("pandas required")
    raise


ROOT = os.path.dirname(os.path.dirname(__file__)) if __file__ else os.getcwd()
MONTHLY_DIR = os.path.join(ROOT, "data/raw/EURUSD/1m_monthly")
PROGRESS_FILE = os.path.join(ROOT, "artifacts/monthly_ai_progress.json")
RESULTS_DIR = os.path.join(ROOT, "artifacts/monthly_ai_results")
LOG_FILE = os.path.join(ROOT, "logs/monthly_ai_pipeline.log")
PID_FILE = "/tmp/monthly_ai.pid"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def write_log(line):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    ts = now_iso()
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} {line}\n")
    print(line)


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {
        "current_month": None,
        "completed_months": [],
        "failed_months": [],
        "last_update": None,
        "percent_complete": 0.0,
    }


def save_progress(p):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    p["last_update"] = now_iso()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(p, f, indent=2)


def limit_cpu_or_nice():
    # If cpulimit available and not already wrapped, re-exec under it.
    from shutil import which
    if which("cpulimit") and os.environ.get("CPULIMIT_WRAPPED") != "1":
        # Re-run under cpulimit -l 10 -- <python> <script> args...
        args = [which("cpulimit"), "-l", "10", "--", sys.executable] + sys.argv
        env = dict(os.environ)
        env["CPULIMIT_WRAPPED"] = "1"
        os.execvpe(args[0], args, env)
    else:
        try:
            os.nice(19)
        except Exception:
            pass


def process_month(file_path, month, progress):
    start = time.time()
    write_log(f"START_MONTH {month}")
    rows = 0
    status = "failed"
    try:
        df = pd.read_parquet(file_path)
        rows = len(df)

        # Simple feature creation: rolling mean/std on 'close' if available
        features_created = 0
        targets_created = 0
        model_metrics = {}

        if "close" in df.columns:
            df = df.sort_values("timestamp")
            df["rmean_5"] = df["close"].rolling(5, min_periods=1).mean()
            df["rstd_5"] = df["close"].rolling(5, min_periods=1).std().fillna(0)
            features_created = 2
            # target: whether next close > current close
            df["target_next_up"] = (df["close"].shift(-1) > df["close"]).astype(int)
            targets_created = 1
            # simple 'model' metric: predict always 0.5 accuracy
            model_metrics = {
                "mean_close": float(df["close"].mean()),
                "std_close": float(df["close"].std()),
                "rows": int(rows),
            }
        else:
            # fallback: no features
            model_metrics = {"note": "no 'close' column"}

        # write results
        os.makedirs(RESULTS_DIR, exist_ok=True)
        out = {
            "month": month,
            "rows": int(rows),
            "features_created": int(features_created),
            "targets_created": int(targets_created),
            "model_metrics": model_metrics,
            "completed_at": now_iso(),
        }
        out_file = os.path.join(RESULTS_DIR, f"{month}.json")
        with open(out_file, "w") as f:
            json.dump(out, f, indent=2)

        status = "done"
    except Exception as e:
        write_log(f"ERROR processing {month}: {e}")
        status = "failed"
    finally:
        end = time.time()
        duration = end - start
        write_log(f"END_MONTH {month} ROWS {rows} DURATION_SECONDS {duration:.2f} STATUS {status}")
        # update progress
        if status == "done":
            progress["completed_months"].append(month)
        else:
            progress["failed_months"].append(month)
        progress["current_month"] = None
        total = len(sorted([f for f in os.listdir(MONTHLY_DIR) if f.endswith('.parquet')]))
        progress["percent_complete"] = round(100.0 * len(progress["completed_months"]) / total, 2) if total else 0.0
        save_progress(progress)

        # free memory
        try:
            del df
        except Exception:
            pass
        gc.collect()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--monthly-dir", default=MONTHLY_DIR)
    args = parser.parse_args()

    limit_cpu_or_nice()

    # single master PID
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                old = int(f.read().strip())
            # check if alive
            os.kill(old, 0)
            print(f"Another pipeline is running with PID {old}. Exiting.")
            return 1
        except Exception:
            # stale PID file
            pass

    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    progress = load_progress()

    files = sorted([f for f in os.listdir(args.monthly_dir) if f.endswith('.parquet')])
    months = [os.path.splitext(f)[0] for f in files]

    # Determine resume point
    completed = set(progress.get("completed_months", []))
    failed = set(progress.get("failed_months", []))

    to_process = [m for m in months if m not in completed]

    total = len(months)
    write_log(f"PIPELINE_START pid={os.getpid()} months={total} start={months[0] if months else 'N/A'} end={months[-1] if months else 'N/A'}")

    for m in to_process:
        path = os.path.join(args.monthly_dir, f"{m}.parquet")
        progress["current_month"] = m
        save_progress(progress)
        process_month(path, m, progress)

    write_log(f"PIPELINE_COMPLETE completed={len(progress.get('completed_months',[]))} failed={len(progress.get('failed_months',[]))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
