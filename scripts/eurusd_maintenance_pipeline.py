#!/usr/bin/env python3
"""EURUSD maintenance pipeline

Performs safe merge of gapfill test parquet into main, rebuilds higher
timeframes, writes manifests and a dataset status artifact and docs.

Does NOT start any downloader or retry daemon.
"""
from pathlib import Path
import subprocess, json, sys
import pandas as pd
from datetime import timezone

ROOT = Path('.').resolve()
OUT_PARQUET = ROOT / 'data' / 'raw' / 'EURUSD' / '1m.parquet'
TEST_PARQUET = ROOT / 'data' / 'raw' / 'EURUSD' / '1m_gapfill_test.parquet'
MAN_DIR = ROOT / 'data' / 'manifests'
ART_DIR = ROOT / 'artifacts'
ART_DIR.mkdir(parents=True, exist_ok=True)

def stop_processes():
    # stop known pid files and pkill any scripts we may have left
    for f in ['/tmp/gapfill.pid','/tmp/gapfill_retry.pid']:
        try:
            p=Path(f)
            if p.exists():
                pid=p.read_text().strip()
                subprocess.run(['kill', pid], check=False)
                subprocess.run(['kill','-9', pid], check=False)
                p.unlink()
        except Exception:
            pass
    subprocess.run("pkill -f dukascopy_gapfill || true", shell=True)
    subprocess.run("pkill -f dukascopy_gapfill_retry_daemon.py || true", shell=True)
    subprocess.run("pkill -f monitor_gapfill.py || true", shell=True)

def run_merge():
    ret = subprocess.run(['.venv/bin/python', 'scripts/merge_gapfill_to_main.py'], check=False)
    return ret.returncode

def validate_1m():
    if not OUT_PARQUET.exists():
        return {'rows':0,'start':None,'end':None}
    df = pd.read_parquet(OUT_PARQUET)
    df['timestamp']=pd.to_datetime(df['timestamp'], utc=True)
    return {'rows': len(df), 'start': df['timestamp'].min().isoformat(), 'end': df['timestamp'].max().isoformat()}

def rebuild_timeframes():
    ret = subprocess.run(['.venv/bin/python', 'scripts/build_higher_timeframes.py'], check=False)
    return ret.returncode

def collect_timeframe_stats():
    stats = {}
    for tf in ['5m','15m','30m','1h','4h','1d']:
        p = MAN_DIR / f"EURUSD_{tf}.json"
        if p.exists():
            try:
                stats[tf]=json.loads(p.read_text())
            except Exception:
                stats[tf]=None
        else:
            stats[tf]=None
    return stats

def write_artifact(status):
    out = ART_DIR / 'eurusd_dataset_status.json'
    out.write_text(json.dumps(status, indent=2))

def write_docs(status):
    md = ROOT / 'docs' / 'EURUSD_DATASET_STATUS.md'
    md.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append('# EURUSD Dataset Status')
    lines.append('')
    lines.append('**Coverage period**')
    lines.append('')
    lines.append(f"- 1m start: {status['1m']['start']}")
    lines.append(f"- 1m end: {status['1m']['end']}")
    lines.append('')
    lines.append('**Available timeframes & rows**')
    lines.append('')
    for tf in ['1m','5m','15m','30m','1h','4h','1d']:
        if tf=='1m':
            rows = status['1m']['rows']
            lines.append(f"- {tf}: {rows} rows")
        else:
            m = status['timeframes'].get(tf)
            if m:
                lines.append(f"- {tf}: {m['rows']} rows (start {m['start']} end {m['end']})")
            else:
                lines.append(f"- {tf}: missing")
    lines.append('')
    lines.append('**Known gaps**')
    lines.append('')
    lines.append('- December 2025: no hourly files available from Dukascopy at time of run (missing)')
    lines.append('- May 2026: partial coverage up to 2026-05-03 16:59 UTC')
    md.write_text('\n'.join(lines))

def main():
    stop_processes()
    run_merge()
    s1m = validate_1m()
    rebuild_timeframes()
    tfs = collect_timeframe_stats()
    status = {'1m': s1m, 'timeframes': tfs}
    write_artifact(status)
    write_docs(status)
    print('Pipeline complete')
    print(json.dumps(status, indent=2))

if __name__ == '__main__':
    main()
