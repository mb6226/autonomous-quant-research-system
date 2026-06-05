#!/usr/bin/env python3
"""Split a single 1m parquet into monthly chunk files.

Reads `data/raw/EURUSD/1m.parquet` and writes per-month parquet files
`data/raw/EURUSD/1m_gapfill_part_YYYY-MM.parquet` plus a manifest
`artifacts/eurusd_split_manifest.json` describing produced chunks.

This is intended for the case where you already have a single large
`1m.parquet` (years of data) and want safe, resumable monthly chunks
to use with the gapfill/processing pipeline.
"""
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
MAIN_PARQUET = Path('data/raw/EURUSD/1m.parquet')
OUT_DIR = Path('data/raw/EURUSD')
OUT_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST = Path('artifacts/eurusd_split_manifest.json')

def atomic_write(df, target_path):
    tmp = target_path.with_suffix('.parquet.tmp')
    df.to_parquet(tmp, index=False)
    try:
        tmp.replace(target_path)
    except Exception:
        tmp.rename(target_path)

def main():
    if not MAIN_PARQUET.exists():
        print('Input main parquet not found:', MAIN_PARQUET)
        return 2
    print('Reading', MAIN_PARQUET)
    df = pd.read_parquet(MAIN_PARQUET)
    if 'timestamp' not in df.columns:
        print('No timestamp column in parquet')
        return 2
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['year_month'] = df['timestamp'].dt.strftime('%Y-%m')

    manifest = {}
    months = sorted(df['year_month'].unique())
    for m in months:
        out_file = OUT_DIR / f'1m_gapfill_part_{m}.parquet'
        sub = df[df['year_month'] == m].drop(columns=['year_month'])
        if len(sub) == 0:
            continue
        print('Writing', out_file, 'rows=', len(sub))
        atomic_write(sub, out_file)
        manifest[m] = {
            'file': str(out_file),
            'rows': int(len(sub)),
            'start_timestamp': sub['timestamp'].min().isoformat(),
            'end_timestamp': sub['timestamp'].max().isoformat()
        }

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST, 'w') as f:
        json.dump({'generated_at': datetime.utcnow().isoformat(), 'chunks': manifest}, f, indent=2)

    print('Split complete. Manifest written to', MANIFEST)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
