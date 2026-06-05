#!/usr/bin/env python3
"""Monitor the monthly AI pipeline and print status every 60 seconds.

Reads artifacts/monthly_ai_progress.json and /tmp/monthly_ai.pid to report:
current_month, completed_count, remaining_count, cpu_usage, memory_usage, eta
"""
import os
import time
import json
from datetime import datetime

PROGRESS_FILE = "artifacts/monthly_ai_progress.json"
PID_FILE = "/tmp/monthly_ai.pid"


def read_progress():
    if not os.path.exists(PROGRESS_FILE):
        return None
    with open(PROGRESS_FILE) as f:
        return json.load(f)


def read_pid():
    if not os.path.exists(PID_FILE):
        return None
    try:
        with open(PID_FILE) as f:
            return int(f.read().strip())
    except Exception:
        return None


def format_ts(ts):
    try:
        return datetime.fromisoformat(ts).isoformat()
    except Exception:
        return str(ts)


def main():
    try:
        import psutil
        ps = psutil
    except Exception:
        ps = None

    while True:
        prog = read_progress()
        pid = read_pid()
        if prog is None:
            print("No progress file yet")
        else:
            current = prog.get("current_month")
            completed = len(prog.get("completed_months", []))
            failed = len(prog.get("failed_months", []))
            percent = prog.get("percent_complete")
            total = completed + failed
            remaining = max(0, (195 - completed))
            print(f"current_month={current} completed={completed} failed={failed} percent={percent} remaining={remaining}")

        if pid and ps:
            try:
                p = ps.Process(pid)
                cpu = p.cpu_percent(interval=0.1)
                mem = p.memory_info().rss
                print(f"pid={pid} cpu%={cpu} mem_rss={mem}")
            except Exception as e:
                print(f"Process {pid} not found: {e}")

        time.sleep(60)


if __name__ == "__main__":
    main()
