#!/usr/bin/env python3
"""Split data/raw/EURUSD/1m.parquet into monthly parquet files.

Writes files to data/raw/EURUSD/1m_monthly/{YYYY-MM}.parquet
Creates artifacts/eurusd_monthly_partition_report.json

Requirements satisfied:
- reads source once
- filters, sorts, writes per-month files
"""
import os
import json
import argparse
from collections import OrderedDict
import pandas as pd
from datetime import timezone


SRC = "data/raw/EURUSD/1m.parquet"
OUT_DIR = "data/raw/EURUSD/1m_monthly"
REPORT = "artifacts/eurusd_monthly_partition_report.json"


def ensure_dirs():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)


def month_key(ts):
    return ts.strftime("%Y-%m")


def human_size_bytes(n):
    for unit in ["B","KB","MB","GB"]:
        if n < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}TB"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", default=SRC)
    p.add_argument("--out-dir", default=OUT_DIR)
    p.add_argument("--report", default=REPORT)
    args = p.parse_args()

    src = args.src
    out_dir = args.out_dir
    report_path = args.report

    if not os.path.exists(src):
        raise SystemExit(f"Source file not found: {src}")

    ensure_dirs()

    print(f"Reading source parquet once: {src}")
    df = pd.read_parquet(src)
    source_rows = len(df)
    print(f"Source rows: {source_rows}")

    if "timestamp" not in df.columns:
        raise SystemExit("Source parquet missing 'timestamp' column")

    # normalize timestamp dtype
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["month"] = df["timestamp"].dt.strftime("%Y-%m")

    months = sorted(df["month"].unique())
    files = []
    partition_rows = 0

    for m in months:
        out_file = os.path.join(out_dir, f"{m}.parquet")
        print(f"Processing month {m}")
        sub = df[df["month"] == m].sort_values("timestamp")
        rows = len(sub)
        if rows == 0:
            print(f"Skipping empty month {m}")
            continue
        # write atomically
        tmp = out_file + ".tmp"
        sub.to_parquet(tmp, index=False)
        os.replace(tmp, out_file)

        start_ts = sub["timestamp"].iloc[0].isoformat()
        end_ts = sub["timestamp"].iloc[-1].isoformat()
        size_bytes = os.path.getsize(out_file)
        files.append({
            "month": m,
            "rows": rows,
            "start_timestamp": start_ts,
            "end_timestamp": end_ts,
            "file": os.path.relpath(out_file),
            "size_bytes": size_bytes,
        })
        partition_rows += rows

    report = OrderedDict()
    report["source_rows"] = source_rows
    report["partition_rows"] = partition_rows
    report["difference"] = partition_rows - source_rows
    report["months_created"] = len(files)
    report["first_month"] = months[0] if months else None
    report["last_month"] = months[-1] if months else None
    report["files"] = files

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # summary report
    print("--- Partitioning complete ---")
    print(f"Source rows: {source_rows}")
    print(f"Partition rows: {partition_rows}")
    print(f"Difference: {report['difference']}")
    print(f"Months created: {report['months_created']}")

    # additional stats
    if files:
        largest = max(files, key=lambda x: x["rows"])
        smallest = min(files, key=lambda x: x["rows"])
        total_bytes = sum(x["size_bytes"] for x in files)
        print(f"Largest month: {largest['month']} rows={largest['rows']}")
        print(f"Smallest month: {smallest['month']} rows={smallest['rows']}")
        print(f"Monthly folder disk usage: {human_size_bytes(total_bytes)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
