#!/usr/bin/env python3
"""Build higher timeframe parquets from merged 1m parquet for EURUSD.

Produces: 5m,15m,30m,1h,4h,1d parquets under data/raw/EURUSD/ and manifests under data/manifests/.
"""
from pathlib import Path
import pandas as pd
import json

ROOT = Path('.').resolve()
IN_PARQUET = ROOT / 'data' / 'raw' / 'EURUSD' / '1m.parquet'
OUT_DIR = ROOT / 'data' / 'raw' / 'EURUSD'
MAN_DIR = ROOT / 'data' / 'manifests'
OUT_DIR.mkdir(parents=True, exist_ok=True)
MAN_DIR.mkdir(parents=True, exist_ok=True)

TF_RULES = {
    '5m': '5min',
    '15m': '15min',
    '30m': '30min',
    '1h': '1h',
    '4h': '4h',
    '1d': '1d',
}

def resample_df(df, rule):
    df = df.sort_values('timestamp').drop_duplicates(subset=['timestamp'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.set_index('timestamp')

    # determine price source
    if 'close' in df.columns:
        price = df['close']
    elif 'price' in df.columns:
        price = df['price']
    else:
        # try open column
        price = df.iloc[:,0]

    o = price.resample(rule).first()
    h = price.resample(rule).max()
    l = price.resample(rule).min()
    c = price.resample(rule).last()

    if 'volume' in df.columns:
        v = df['volume'].resample(rule).sum()
    else:
        v = pd.Series(0, index=o.index)

    out = pd.DataFrame({'open': o, 'high': h, 'low': l, 'close': c, 'volume': v})
    out = out.dropna(subset=['open']).reset_index()
    return out

def write_parquet_and_manifest(df_out, tf_label):
    out_path = OUT_DIR / f"{tf_label}.parquet"
    tmp = out_path.with_suffix('.tmp.parquet')
    df_out.to_parquet(tmp, index=False)
    tmp.replace(out_path)

    rows = len(df_out)
    start = df_out['timestamp'].min().isoformat() if rows>0 else None
    end = df_out['timestamp'].max().isoformat() if rows>0 else None
    manifest = {
        'symbol': 'EURUSD',
        'timeframe': tf_label,
        'rows': rows,
        'start': start,
        'end': end,
    }
    man_path = MAN_DIR / f"EURUSD_{tf_label}.json"
    with open(man_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f'Wrote {out_path} rows={rows} start={start} end={end}')
    return manifest

def main():
    if not IN_PARQUET.exists():
        print('Input parquet not found:', IN_PARQUET)
        return

    df = pd.read_parquet(IN_PARQUET)
    if 'timestamp' not in df.columns:
        print('No timestamp column in input parquet')
        return

    results = {}
    for tf_label, rule in TF_RULES.items():
        out_df = resample_df(df.copy(), rule)
        manifest = write_parquet_and_manifest(out_df, tf_label)
        results[tf_label] = manifest

    # write an overall summary
    summary_path = MAN_DIR / 'EURUSD_higher_timeframes_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    print('Done. Summary written to', summary_path)

if __name__ == '__main__':
    main()
