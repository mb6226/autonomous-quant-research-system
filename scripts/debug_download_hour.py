#!/usr/bin/env python3
"""Debug script: download and resample a single Dukascopy hour without writing parquet.

Usage: scripts/debug_download_hour.py YYYY-MM-DD HOUR
"""
from pathlib import Path
from datetime import datetime, timezone
import sys
import struct
import lzma, zlib, bz2, gzip
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.providers.dukascopy.downloader import DukascopyDownloader

def decompress_content(content):
    for fn in (lzma.decompress, zlib.decompress, bz2.decompress, gzip.decompress):
        try:
            return fn(content)
        except Exception:
            continue
    return None

SCALE = 100000.0
FMT = '>IIIff'

def run_debug(date_str, hour):
    duk = DukascopyDownloader(symbol='EURUSD')
    session = duk.session
    d = datetime.fromisoformat(date_str).date()
    url = duk._hour_url(d.year, d.month, d.day, hour)
    print('URL:', url)
    try:
        r = session.get(url, timeout=30)
    except Exception as e:
        print('HTTP error:', e)
        return 1
    print('HTTP status:', getattr(r, 'status_code', None))
    if r.status_code != 200:
        print('No data (status != 200)')
        return 2
    content = r.content
    dec = decompress_content(content)
    if dec is None or len(dec) < 20:
        print('No decompressed data / too short')
        return 3
    ticks = []
    for i in range(0, len(dec)//20 * 20, 20):
        chunk = dec[i:i+20]
        try:
            ms_from_hour, ask_u, bid_u, ask_vol, bid_vol = struct.unpack(FMT, chunk)
        except struct.error:
            continue
        ticks.append((int(ms_from_hour), int(ask_u), int(bid_u), float(ask_vol), float(bid_vol)))
    print('ticks:', len(ticks))
    if not ticks:
        return 4
    hour_start = pd.to_datetime(datetime(d.year, d.month, d.day, hour, tzinfo=timezone.utc))
    rows = []
    for (ms, ask_u, bid_u, ask_vol, bid_vol) in ticks:
        ts = hour_start + pd.to_timedelta(ms, unit='ms')
        ask = ask_u / SCALE
        bid = bid_u / SCALE
        price = (bid + ask) / 2.0
        vol = (bid_vol if bid_vol==bid_vol else 0.0) + (ask_vol if ask_vol==ask_vol else 0.0)
        rows.append((ts, price, vol))
    tdf = pd.DataFrame(rows, columns=['timestamp','price','volume']).set_index('timestamp')
    ohlc = tdf['price'].resample('1min').agg(['first','max','min','last'])
    volsum = tdf['volume'].resample('1min').sum()
    ohlc = ohlc.rename(columns={'first':'open','max':'high','min':'low','last':'close'})
    ohlc['volume'] = volsum
    ohlc = ohlc.dropna(subset=['open']).reset_index()
    print('minute_rows_generated:', len(ohlc))
    if not ohlc.empty:
        print(ohlc.head().to_string(index=False))
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: debug_download_hour.py YYYY-MM-DD HOUR')
        sys.exit(1)
    date_str = sys.argv[1]
    hour = int(sys.argv[2])
    sys.exit(run_debug(date_str, hour))
