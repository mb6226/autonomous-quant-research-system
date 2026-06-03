#!/usr/bin/env python3
"""Lightweight monitor for the running gap-fill.

Reads `data/raw/EURUSD/1m_gapfill_test.parquet` every 5 minutes and reports:
- rows
- start_timestamp
- end_timestamp
- file_size_mb
- estimated_completion (based on expected rows)

Writes status to `artifacts/eurusd_gapfill_monitor.json` and keeps a small state to
estimate rate and remaining time.
"""
import time, json, os
from pathlib import Path
import pandas as pd
from datetime import datetime

OUT_PARQUET = Path('data/raw/EURUSD/1m_gapfill_test.parquet')
ART_MON = Path('artifacts/eurusd_gapfill_monitor.json')
STATE = Path('artifacts/eurusd_gapfill_monitor_state.json')

# Expected new rows for full gap-fill (from plan)
EXPECTED_ROWS = 1272960

def read_parquet_stats():
    if not OUT_PARQUET.exists():
        return {'rows':0,'start_timestamp':None,'end_timestamp':None,'file_size_mb':0.0}
    try:
        df = pd.read_parquet(OUT_PARQUET)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        rows = len(df)
        s = df['timestamp'].min().isoformat() if rows>0 else None
        e = df['timestamp'].max().isoformat() if rows>0 else None
        size_mb = OUT_PARQUET.stat().st_size / 1024 / 1024
        return {'rows':int(rows),'start_timestamp':s,'end_timestamp':e,'file_size_mb':round(size_mb,3)}
    except Exception:
        return {'rows':0,'start_timestamp':None,'end_timestamp':None,'file_size_mb':round(OUT_PARQUET.stat().st_size/1024/1024,3) if OUT_PARQUET.exists() else 0.0}

def load_state():
    if not STATE.exists():
        return {'ts': None, 'rows': 0, 'consecutive_zero': 0, 'checks': 0}
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {'ts': None, 'rows': 0, 'consecutive_zero': 0, 'checks': 0}

def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s))

def save_monitor(m):
    ART_MON.parent.mkdir(parents=True, exist_ok=True)
    ART_MON.write_text(json.dumps(m, indent=2, default=str))

def estimate(now_rows, prev):
    # compute rows_added_since_last_check and growth rate
    if prev['ts'] is None:
        return {'rows_added_since_last_check': now_rows - prev['rows'], 'growth_rate_rows_per_sec': None, 'eta_seconds': None}
    dt = time.time() - prev['ts']
    drows = now_rows - prev['rows']
    rate = drows / dt if dt>0 else None
    remaining = max(0, EXPECTED_ROWS - now_rows)
    eta = int(remaining / rate) if rate and rate>0 else None
    return {'rows_added_since_last_check': int(drows), 'growth_rate_rows_per_sec': round(rate,3) if rate is not None else None, 'eta_seconds': eta}

def main():
    state = load_state()
    while True:
        stats = read_parquet_stats()
        est = estimate(stats['rows'], state)

        # update consecutive zero checks
        if est['rows_added_since_last_check'] == 0:
            state['consecutive_zero'] = state.get('consecutive_zero', 0) + 1
        else:
            state['consecutive_zero'] = 0

        state['checks'] = state.get('checks', 0) + 1
        # prepare monitor payload
        payload = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'rows': int(stats['rows']),
            'rows_added_since_last_check': int(est['rows_added_since_last_check']) if est['rows_added_since_last_check'] is not None else None,
            'start_timestamp': stats['start_timestamp'],
            'end_timestamp': stats['end_timestamp'],
            'file_size_mb': stats['file_size_mb'],
            'growth_rate_rows_per_sec': est['growth_rate_rows_per_sec'],
            'estimated_completion_time': (datetime.utcnow() + pd.to_timedelta(est['eta_seconds'], unit='s')).isoformat() + 'Z' if est.get('eta_seconds') else None,
            'consecutive_zero_checks': int(state['consecutive_zero'])
        }

        # alert on 3 consecutive zero-growth checks
        if state['consecutive_zero'] >= 3:
            payload['alert'] = 'POSSIBLE STALL'

        save_monitor(payload)

        # hourly print (every 12 checks of 5 minutes)
        if state['checks'] % 12 == 0:
            est_final_rows = EXPECTED_ROWS
            print('HOURLY:', stats['rows'], stats['file_size_mb'], est_final_rows, payload['estimated_completion_time'])

        # persist state
        state['ts'] = time.time()
        state['rows'] = int(stats['rows'])
        save_state(state)

        # print succinct output to stdout for immediate visibility
        print(json.dumps(payload))
        # sleep 5 minutes
        time.sleep(300)

if __name__ == '__main__':
    main()
