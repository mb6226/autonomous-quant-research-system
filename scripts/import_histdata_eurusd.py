#!/usr/bin/env python3
"""Import HistData EURUSD M1 Excel into AQRS parquet+manifest.

Usage: python3 scripts/import_histdata_eurusd.py
"""
import json
from pathlib import Path
import pandas as pd


IN_FILE = Path("data/raw/EURUSD/source/DAT_XLSX_EURUSD_M1_2010.xlsx")
OUT_PARQUET = Path("data/raw/EURUSD/1m.parquet")
MANIFEST = Path("data/manifests/EURUSD_1m.json")


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        # Some Excel files have non-string column headers (datetime, NaN); coerce to str
        cname = str(c) if not isinstance(c, str) else c
        key = cname.lower().strip()
        if "date" in key and "time" not in key:
            rename[c] = "date"
        elif "time" in key and "date" not in key:
            rename[c] = "time"
        elif key in ("datetime", "date_time", "date/time"):
            rename[c] = "datetime"
        elif key.startswith("open"):
            rename[c] = "open"
        elif key.startswith("high"):
            rename[c] = "high"
        elif key.startswith("low"):
            rename[c] = "low"
        elif key.startswith("close"):
            rename[c] = "close"
        elif "vol" in key:
            rename[c] = "volume"
    return df.rename(columns=rename)


def build_timestamp(df: pd.DataFrame) -> pd.Series:
    if "datetime" in df.columns:
        ts = pd.to_datetime(df["datetime"], errors="coerce", utc=True)
    elif "time" in df.columns:
        ts = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str), errors="coerce", utc=True)
    else:
        ts = pd.to_datetime(df["date"], errors="coerce", utc=True)
    return ts


def main():
    if not IN_FILE.exists():
        raise SystemExit(f"Input file not found: {IN_FILE}")

    df = pd.read_excel(IN_FILE)
    df = normalize_column_names(df)

    # If normalization didn't find OHLCV (common when file has no header),
    # re-read treating the sheet as headerless and assign expected columns.
    expected = ("date", "open", "high", "low", "close", "volume")
    if not all(col in df.columns for col in ("open", "high", "low", "close")):
        df = pd.read_excel(IN_FILE, header=None)
        if df.shape[1] < 5:
            raise SystemExit("Excel file has unexpected number of columns for M1 data")
        # take first 6 columns as date,open,high,low,close,volume
        cols = list(df.columns[:6])
        df = df.iloc[:, :6]
        df.columns = list(expected)

    ts = build_timestamp(df)
    df["timestamp"] = ts

    # Drop rows with invalid timestamps
    df = df[~df["timestamp"].isna()].copy()

    # Normalize numeric columns
    for col in ("open", "high", "low", "close", "volume"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Keep only final columns
    out_cols = ["timestamp", "open", "high", "low", "close", "volume"]
    for c in out_cols:
        if c not in df.columns:
            df[c] = pd.NA

    df = df[out_cols]

    # Ensure UTC tz and sort
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp")

    # Drop duplicate timestamps
    df = df.drop_duplicates(subset=["timestamp"], keep="first")

    # Ensure output directory exists
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    # Write parquet
    df.to_parquet(OUT_PARQUET, engine="pyarrow", index=False)

    # Manifest
    rows = int(len(df))
    start = df["timestamp"].min()
    end = df["timestamp"].max()

    def iso_z(ts):
        if pd.isna(ts):
            return None
        ts = pd.to_datetime(ts, utc=True)
        return ts.strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "market": "EURUSD",
        "timeframe": "1m",
        "rows": rows,
        "start_date": iso_z(start),
        "end_date": iso_z(end),
    }

    with MANIFEST.open("w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    # Print required info: rows, start_date, end_date
    print(rows)
    print(manifest["start_date"])
    print(manifest["end_date"]) 


if __name__ == "__main__":
    main()
