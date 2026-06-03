#!/usr/bin/env python3
"""Controlled dry run: download Dukascopy hours for 2024-01 (one month), parse ticks, aggregate to 1m,
write to data/raw/EURUSD/1m_gapfill_test.parquet and produce artifacts/dukascopy_dry_run_report.json

Do NOT modify production parquet or start other months.
"""
from pathlib import Path
from datetime import datetime, timezone
import lzma, zlib, bz2, gzip, struct, json
import pandas as pd
import requests

import sys
from pathlib import Path as _P
ROOT = _P(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.providers.dukascopy.downloader import DukascopyDownloader

OUT_PARQUET = Path('data/raw/EURUSD/1m_gapfill_test.parquet')
ARTIFACT = Path('artifacts/dukascopy_dry_run_report.json')

START = datetime(2024,1,1,tzinfo=timezone.utc)
END = datetime(2024,1,31,tzinfo=timezone.utc)

duk = DukascopyDownloader(symbol='EURUSD')
session = duk.session

hours_downloaded = 0
files_downloaded = 0
ticks_processed = 0
minute_rows_generated = 0

all_minutes = []

SCALE = 100000.0
FMT = '>IIIff'

for day in range(1, 32):
    for hour in range(24):
        year = 2024; month = 1; dayv = day; hourv = hour
        url = duk._hour_url(year, month, dayv, hourv)
        try:
            r = session.get(url, timeout=30)
        except Exception:
            continue
        if r.status_code != 200:
            continue
        files_downloaded += 1
        content = r.content
        decompressed = None
        for name, fn in (('lzma', lzma.decompress), ('zlib', zlib.decompress), ('bz2', bz2.decompress), ('gzip', gzip.decompress)):
            try:
                out = fn(content)
                decompressed = out
                break
            except Exception:
                decompressed = None
        if decompressed is None:
            # couldn't decompress
            continue
        if len(decompressed) < 20:
            continue
        # if binary ticks
        if len(decompressed) % 20 != 0:
            # still attempt to parse by trimming
            pass
        ticks = []
        for i in range(0, len(decompressed)//20 * 20, 20):
            chunk = decompressed[i:i+20]
            try:
                ms_from_hour, ask_u, bid_u, ask_vol, bid_vol = struct.unpack(FMT, chunk)
            except struct.error:
                continue
            ticks.append((int(ms_from_hour), int(ask_u), int(bid_u), float(ask_vol), float(bid_vol)))
        tick_count = len(ticks)
        ticks_processed += tick_count
        if tick_count == 0:
            continue
        # build records
        # reconstruct hour start
        hour_start = pd.to_datetime(datetime(year, month, dayv, hourv, tzinfo=timezone.utc))
        rows = []
        for (ms, ask_u, bid_u, ask_vol, bid_vol) in ticks:
            ts = hour_start + pd.to_timedelta(ms, unit='ms')
            ask = ask_u / SCALE
            bid = bid_u / SCALE
            price = (bid + ask)/2.0
            vol = (bid_vol if bid_vol==bid_vol else 0.0) + (ask_vol if ask_vol==ask_vol else 0.0)
            rows.append((ts, price, vol))
        if not rows:
            continue
        tdf = pd.DataFrame(rows, columns=['timestamp','price','volume']).set_index('timestamp')
        ohlc = tdf['price'].resample('1min').agg(['first','max','min','last'])
        volsum = tdf['volume'].resample('1min').sum()
        ohlc = ohlc.rename(columns={'first':'open','max':'high','min':'low','last':'close'})
        ohlc['volume'] = volsum
        ohlc = ohlc.dropna(subset=['open']).reset_index()
        minute_rows_generated += len(ohlc)
        all_minutes.append(ohlc)
        hours_downloaded += 1

# combine
if all_minutes:
    combined = pd.concat(all_minutes, ignore_index=True)
    before = len(combined)
    combined['timestamp'] = pd.to_datetime(combined['timestamp'], utc=True)
    combined = combined.sort_values('timestamp').reset_index(drop=True)
    combined = combined.drop_duplicates(subset=['timestamp'], keep='first')
    after = len(combined)
    duplicates_removed = before - after
    combined.to_parquet(OUT_PARQUET, index=False)
    parquet_size_mb = OUT_PARQUET.stat().st_size / 1024 / 1024
    start_ts = combined['timestamp'].min().isoformat()
    end_ts = combined['timestamp'].max().isoformat()
else:
    combined = pd.DataFrame(columns=['timestamp','open','high','low','close','volume'])
    duplicates_removed = 0
    parquet_size_mb = 0.0
    start_ts = None
    end_ts = None

report = {
    'hours_downloaded': hours_downloaded,
    'files_downloaded': files_downloaded,
    'ticks_processed': ticks_processed,
    'minute_rows_generated': minute_rows_generated,
    'duplicates_removed': duplicates_removed,
    'start_timestamp': start_ts,
    'end_timestamp': end_ts,
    'parquet_size_mb': round(parquet_size_mb, 3)
}
ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
with open(ARTIFACT, 'w') as f:
    json.dump(report, f, indent=2)

print('Dry run complete')
print(report)

# exit non-zero if no hours downloaded
if hours_downloaded == 0:
    raise SystemExit(2)
