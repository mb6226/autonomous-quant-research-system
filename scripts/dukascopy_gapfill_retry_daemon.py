#!/usr/bin/env python3
"""Daemon that periodically retries missing hourly Dukascopy files

It attempts to download any missing hours between configured START_DATE and
END_DATE and appends newly-available minute bars to `data/raw/EURUSD/1m_gapfill_test.parquet`.

Configure `INTERVAL_HOURS` to control how often the full pass repeats.
"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import time, json
import pandas as pd
import sys, os

from app.data.providers.dukascopy.downloader import DukascopyDownloader

OUT_PARQUET = Path('data/raw/EURUSD/1m_gapfill_test.parquet')
ART_PROGRESS = Path('artifacts/eurusd_gapfill_progress.json')

# Range to monitor (inclusive start, exclusive end)
START_DATE = datetime(2025,5,1, tzinfo=timezone.utc)
END_DATE = datetime(2026,6,1, tzinfo=timezone.utc)

# Hours between full-pass retries
INTERVAL_HOURS = 24

def hours_range(start_dt, end_dt):
    cur = start_dt.replace(minute=0, second=0, microsecond=0)
    while cur < end_dt:
        yield cur
        cur += timedelta(hours=1)

def load_parquet_hours():
    if not OUT_PARQUET.exists():
        return set()
    try:
        df = pd.read_parquet(OUT_PARQUET, columns=['timestamp'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        hours = set(df['timestamp'].dt.floor('H').drop_duplicates().astype(str).tolist())
        return hours
    except Exception:
        return set()

def append_minutes_to_parquet(df_minutes: pd.DataFrame):
    # atomic write: write to tmp then replace
    tmp = OUT_PARQUET.with_suffix('.tmp.parquet')
    if OUT_PARQUET.exists():
        try:
            old = pd.read_parquet(OUT_PARQUET)
            combined = pd.concat([old, df_minutes], ignore_index=True)
        except Exception:
            combined = df_minutes
    else:
        combined = df_minutes

    if 'timestamp' in combined.columns:
        combined['timestamp'] = pd.to_datetime(combined['timestamp'], utc=True)
        combined = combined.drop_duplicates(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)

    combined.to_parquet(tmp, index=False)
    tmp.replace(OUT_PARQUET)

def load_progress():
    if ART_PROGRESS.exists():
        try:
            return json.loads(ART_PROGRESS.read_text())
        except Exception:
            return {'retries': []}
    return {'retries': []}

def save_progress(progress):
    ART_PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    ART_PROGRESS.write_text(json.dumps(progress, indent=2))

def main_loop():
    duk = DukascopyDownloader('EURUSD')
    progress = load_progress()

    while True:
        print(f"Retry pass start: {datetime.now(timezone.utc).isoformat()}")
        existing_hours = load_parquet_hours()
        missing = []
        for h in hours_range(START_DATE, END_DATE):
            hstr = h.isoformat()
            if hstr not in existing_hours:
                missing.append(h)

        print(f"Missing hours to try: {len(missing)}")

        for h in missing:
            y,mo,d,hr = h.year, h.month, h.day, h.hour
            hstr = h.isoformat()
            print('Trying', hstr)
            try:
                df = duk.download_hour(y, mo, d, hr)
                if df is None or df.empty:
                    # record failure
                    progress['retries'].append({'hour': hstr, 'status': 'missing'})
                    save_progress(progress)
                    continue
                # ensure timestamp col exists
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
                append_minutes_to_parquet(df)
                progress['retries'].append({'hour': hstr, 'status': 'added', 'rows': len(df)})
                save_progress(progress)
                print('Appended', len(df), 'rows for', hstr)
                # update existing_hours to avoid repeated downloads this pass
                existing_hours.add(hstr)
            except Exception as e:
                progress['retries'].append({'hour': hstr, 'status': 'error', 'error': str(e)})
                save_progress(progress)
                print('Error for', hstr, e)
            # be polite
            time.sleep(0.2)

        print('Retry pass complete; sleeping', INTERVAL_HOURS, 'hours')
        time.sleep(INTERVAL_HOURS * 3600)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('Daemon stopped by user')
