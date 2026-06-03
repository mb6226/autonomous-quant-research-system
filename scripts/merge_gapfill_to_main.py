#!/usr/bin/env python3
"""Safely stop gap-fill runner and merge test parquet into main 1m.parquet.

Usage: run under project venv (no args):
  .venv/bin/python scripts/merge_gapfill_to_main.py

This script will:
- stop the running gapfill process referenced in /tmp/gapfill.pid (TERM then KILL)
- backup existing `data/raw/EURUSD/1m.parquet` to `artifacts/` with timestamp
- read both parquets, concat, dedupe on `timestamp`, sort, and atomically overwrite main parquet
- print resulting row count and max timestamp

DO NOT RUN THIS UNLESS YOU WANT TO MERGE TEST DATA INTO PRODUCTION.
"""
import os
import signal
import shutil
from pathlib import Path
from datetime import datetime
import sys

PIDFILE = Path('/tmp/gapfill.pid')
MAIN_PARQUET = Path('data/raw/EURUSD/1m.parquet')
TEST_PARQUET = Path('data/raw/EURUSD/1m_gapfill_test.parquet')
ARTIFACTS_DIR = Path('artifacts')
ARTIFACTS_DIR.mkdir(exist_ok=True)

def stop_runner():
    if PIDFILE.exists():
        try:
            pid = int(PIDFILE.read_text().strip())
        except Exception:
            print('Could not read PID from', PIDFILE)
            return
        print('Stopping PID', pid)
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            print('Process not found (already stopped)')
        except PermissionError:
            print('PermissionError sending TERM to', pid)
        # wait briefly
        import time
        time.sleep(3)
        # check
        try:
            os.kill(pid, 0)
            print('Process still alive; sending KILL')
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception as e:
                print('Failed to KILL:', e)
        except ProcessLookupError:
            print('Process stopped')
    else:
        print('No pidfile', PIDFILE)

def backup_main():
    if MAIN_PARQUET.exists():
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        dest = ARTIFACTS_DIR / f'1m.parquet.backup.{ts}.parquet'
        print('Backing up', MAIN_PARQUET, 'to', dest)
        shutil.copy2(MAIN_PARQUET, dest)
        return dest
    else:
        print('No existing main parquet to backup')
        return None

def merge_parquets():
    try:
        import pandas as pd
    except Exception as e:
        print('pandas not available in this environment:', e)
        return False

    if not TEST_PARQUET.exists():
        print('Test parquet not found:', TEST_PARQUET)
        return False

    print('Reading test parquet:', TEST_PARQUET)
    df_test = pd.read_parquet(TEST_PARQUET)
    if 'timestamp' in df_test.columns:
        df_test['timestamp'] = pd.to_datetime(df_test['timestamp'], utc=True)
    else:
        print('Test parquet missing timestamp column')
        return False

    if MAIN_PARQUET.exists():
        print('Reading main parquet:', MAIN_PARQUET)
        df_main = pd.read_parquet(MAIN_PARQUET)
        if 'timestamp' in df_main.columns:
            df_main['timestamp'] = pd.to_datetime(df_main['timestamp'], utc=True)
        else:
            print('Main parquet missing timestamp column')
            return False
    else:
        df_main = None

    if df_main is None or df_main.empty:
        combined = df_test.copy()
    else:
        combined = pd.concat([df_main, df_test], ignore_index=True)

    before = len(combined)
    combined = combined.drop_duplicates(subset=['timestamp'], keep='first')
    combined = combined.sort_values('timestamp').reset_index(drop=True)
    after = len(combined)
    print(f'Rows before dedupe: {before}, after dedupe: {after}')

    # atomic write
    tmp = MAIN_PARQUET.with_suffix('.tmp.parquet')
    combined.to_parquet(tmp, index=False)
    tmp.replace(MAIN_PARQUET)
    final_rows = len(combined)
    final_end_ts = combined['timestamp'].max()
    print('Wrote merged parquet to', MAIN_PARQUET)
    print('Merged rows:', final_rows)
    print('Merged end timestamp:', final_end_ts)
    return True

if __name__ == '__main__':
    print('*** MERGE GAPFILL INTO MAIN - STARTING')
    stop_runner()
    backup_main()
    ok = merge_parquets()
    if not ok:
        print('Merge failed or skipped')
        sys.exit(2)
    print('*** MERGE COMPLETE')
