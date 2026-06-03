#!/usr/bin/env python3
"""Import all HistData EURUSD M1 Excel files from source folder into AQRS parquet.

This script scans `data/raw/EURUSD/source` for files matching
`DAT_XLSX_EURUSD_M1_*.xlsx`, reads each workbook, normalizes columns,
builds UTC timestamps, concatenates with existing `data/raw/EURUSD/1m.parquet`,
deduplicates on `timestamp`, writes the parquet and updates the manifest.

Usage: python3 scripts/import_all_histdata_eurusd.py
"""
from pathlib import Path
import json
import pandas as pd


SRC_DIR = Path("data/raw/EURUSD/source")
OUT_PARQUET = Path("data/raw/EURUSD/1m.parquet")
MANIFEST = Path("data/manifests/EURUSD_1m.json")


def read_hist_xlsx(p: Path) -> pd.DataFrame:
    df = pd.read_excel(p)
    # coerce column names to strings
    df.columns = [str(c) for c in df.columns]
    # detect headerless (first column looks numeric/date rather than text)
    col0 = df.columns[0]
    if not any(x in str(col0).lower() for x in ['date','time','open','close','high','vol']):
        df = pd.read_excel(p, header=None)
        df = df.iloc[:, :6]
        df.columns = ['date','open','high','low','close','volume']
        return df

    # normalize names
    rename = {}
    for c in df.columns:
        k = str(c).lower()
        if 'date' in k and 'time' not in k:
            rename[c] = 'date'
        elif 'time' in k and 'date' not in k:
            rename[c] = 'time'
        elif k in ('datetime','date_time','date/time'):
            rename[c] = 'datetime'
        elif k.startswith('open'):
            rename[c] = 'open'
        elif k.startswith('high'):
            rename[c] = 'high'
        elif k.startswith('low'):
            rename[c] = 'low'
        elif k.startswith('close'):
            rename[c] = 'close'
        elif 'vol' in k:
            rename[c] = 'volume'
    df = df.rename(columns=rename)

    expected = ('date','open','high','low','close','volume')
    if not all(col in df.columns for col in ('open','high','low','close')):
        df = pd.read_excel(p, header=None)
        df = df.iloc[:, :6]
        df.columns = list(expected)
    return df


def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    if 'datetime' in df.columns:
        ts = pd.to_datetime(df['datetime'], errors='coerce', utc=True)
    elif 'time' in df.columns:
        ts = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str), errors='coerce', utc=True)
    else:
        ts = pd.to_datetime(df['date'], errors='coerce', utc=True)
    df['timestamp'] = ts
    df = df[~df['timestamp'].isna()].copy()
    for col in ('open','high','low','close','volume'):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df[['timestamp','open','high','low','close','volume']]
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.sort_values('timestamp')
    df = df.drop_duplicates(subset=['timestamp'], keep='first')
    return df


def main():
    files = sorted(SRC_DIR.glob('DAT_XLSX_EURUSD_M1_*.xlsx'))
    if not files:
        print('No source files found in', SRC_DIR)
        return

    frames = []
    for f in files:
        print('Reading', f)
        df = read_hist_xlsx(f)
        df = prepare_df(df)
        frames.append(df)

    if frames:
        new = pd.concat(frames, ignore_index=True)
    else:
        new = pd.DataFrame(columns=['timestamp','open','high','low','close','volume'])

    if OUT_PARQUET.exists():
        old = pd.read_parquet(OUT_PARQUET)
        combined = pd.concat([old, new], ignore_index=True)
        combined = combined.sort_values('timestamp')
        combined = combined.drop_duplicates(subset=['timestamp'], keep='first')
    else:
        combined = new

    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(OUT_PARQUET, engine='pyarrow', index=False)

    rows = int(len(combined))
    start = combined['timestamp'].min()
    end = combined['timestamp'].max()

    def iso_z(ts):
        if pd.isna(ts):
            return None
        ts = pd.to_datetime(ts, utc=True)
        return ts.strftime('%Y-%m-%dT%H:%M:%SZ')

    manifest = {
        'market': 'EURUSD',
        'timeframe': '1m',
        'rows': rows,
        'start_date': iso_z(start),
        'end_date': iso_z(end),
    }

    with MANIFEST.open('w') as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    print(rows)
    print(manifest['start_date'])
    print(manifest['end_date'])


if __name__ == '__main__':
    main()
