#!/usr/bin/env python3
"""Fill EURUSD M1 gaps from Dukascopy (2024-01-01 -> today) in monthly chunks.

This script appends month-by-month, supports resume, deduplicates, updates manifest,
and prints rows/start_date/end_date after merging.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path
import time
import pandas as pd

# Ensure project root is on sys.path so `from app...` imports succeed when running script directly
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.providers.dukascopy.downloader import DukascopyDownloader


OUT_PARQUET = Path("data/raw/EURUSD/1m.parquet")
MANIFEST = Path("data/manifests/EURUSD_1m.json")


def month_iter(start_dt: datetime, end_dt: datetime):
    cur = datetime(start_dt.year, start_dt.month, 1)
    while cur <= end_dt:
        yield cur.year, cur.month
        if cur.month == 12:
            cur = datetime(cur.year + 1, 1, 1)
        else:
            cur = datetime(cur.year, cur.month + 1, 1)


def normalize_month_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # ensure timestamp column
    if "timestamp" not in df.columns:
        # try first column
        first = df.columns[0]
        try:
            df["timestamp"] = pd.to_datetime(df[first], utc=True, errors="coerce")
        except Exception:
            df["timestamp"] = pd.to_datetime(df[first].astype(str), utc=True, errors="coerce")

    # normalize OHLCV names
    colmap = {}
    for c in df.columns:
        k = str(c).lower()
        if k in ("o","open") or k.startswith("open"):
            colmap[c] = "open"
        elif k in ("h","high") or k.startswith("high"):
            colmap[c] = "high"
        elif k in ("l","low") or k.startswith("low"):
            colmap[c] = "low"
        elif k in ("c","close") or k.startswith("close"):
            colmap[c] = "close"
        elif "vol" in k:
            colmap[c] = "volume"

    if colmap:
        df = df.rename(columns=colmap)

    # ensure final columns exist
    for col in ("open", "high", "low", "close", "volume"):
        if col not in df.columns:
            df[col] = pd.NA

    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])  # drop rows without valid timestamp
    df = df.sort_values("timestamp")
    df = df.drop_duplicates(subset=["timestamp"], keep="first")
    return df


def main():
    duk = DukascopyDownloader(symbol="EURUSD")

    # determine resume start
    earliest = datetime(2024, 1, 1)
    if OUT_PARQUET.exists():
        try:
            existing = pd.read_parquet(OUT_PARQUET)
            existing["timestamp"] = pd.to_datetime(existing["timestamp"], utc=True, errors="coerce")
            max_ts = existing["timestamp"].max()
            if pd.notna(max_ts):
                # start from next minute
                resume_dt = (pd.to_datetime(max_ts) + pd.Timedelta(minutes=1)).to_pydatetime()
            else:
                resume_dt = earliest
        except Exception:
            resume_dt = earliest
    else:
        resume_dt = earliest

    today = datetime.utcnow()
    # if resume_dt is after today, nothing to do
    if resume_dt.date() > today.date():
        print("No new months to download; dataset up-to-date")
        # print summary
        if OUT_PARQUET.exists():
            df = pd.read_parquet(OUT_PARQUET)
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            print(len(df))
            print(df["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ"))
            print(df["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ"))
        return

    start_iter = datetime(resume_dt.year, resume_dt.month, 1)

    for year, month in month_iter(start_iter, today):
        print(f"Processing month {year}-{month:02d}")
        try:
            month_df = duk.download_month(year, month)
            if month_df.empty:
                print(f"No data for {year}-{month:02d}")
                continue

            month_df = normalize_month_df(month_df)
            if month_df.empty:
                print(f"Parsed month empty for {year}-{month:02d}")
                continue

            duk.save_parquet(month_df)
            duk.update_manifest()
            # small delay between months
            time.sleep(0.5)
        except Exception as e:
            print(f"Failed {year}-{month:02d}: {e}")

    # final summary
    if OUT_PARQUET.exists():
        df = pd.read_parquet(OUT_PARQUET)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        print(len(df))
        print(df["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ"))
        print(df["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ"))


if __name__ == "__main__":
    main()
