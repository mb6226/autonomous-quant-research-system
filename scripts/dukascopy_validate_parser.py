#!/usr/bin/env python3
"""Validate Dukascopy parser using ms-offset rule and write artifacts JSON."""
import lzma, struct, json
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone

DEBUG_DIR = Path('data/raw/EURUSD/dukascopy_debug')
ARTIFACT = Path('artifacts/dukascopy_parser_validation.json')

FILES = [
    '2024-01-01-00.bin',
    '2024-01-01-06.bin',
    '2024-01-01-12.bin',
    '2024-01-01-18.bin',
    '2024-02-01-00.bin',
]

SCALE = 100000.0

results = {
    'hours_tested': 0,
    'hours_passed': 0,
    'hours_failed': 0,
    'files': []
}

for fname in FILES:
    fp = DEBUG_DIR / fname
    if not fp.exists():
        print('missing', fname)
        continue
    raw = fp.read_bytes()
    try:
        out = lzma.decompress(raw)
    except Exception as e:
        results['files'].append({'file': fname, 'decompress_attempts': {'lzma': f'fail: {e}'}, 'pass': False})
        results['hours_tested'] += 1
        results['hours_failed'] += 1
        continue

    n = len(out) // 20
    records = []
    hour_start = None
    bad_bid = bad_ask = bad_spread = bad_ts = 0
    for i in range(0, len(out), 20):
        chunk = out[i:i+20]
        if len(chunk) < 20:
            continue
        try:
            ms_from_hour, ask_u, bid_u, ask_vol, bid_vol = struct.unpack('>IIIff', chunk)
        except struct.error:
            continue
        if hour_start is None:
            # parse filename
            parts = fname.split('-')
            yr = int(parts[0]); mo = int(parts[1]); day = int(parts[2]); hr = int(parts[3].split('.')[0])
            hour_start = pd.to_datetime(datetime(yr, mo, day, hr, tzinfo=timezone.utc))
        ms_offset = int(ms_from_hour)
        ts = hour_start + pd.to_timedelta(ms_offset, unit='ms')
        ask = ask_u / SCALE
        bid = bid_u / SCALE
        # validations
        if not (0.5 <= bid <= 2.0):
            bad_bid += 1
        if not (0.5 <= ask <= 2.0):
            bad_ask += 1
        if not (ask > bid and (ask - bid) < 0.01):
            bad_spread += 1
        # timestamp validation: use ms-offset rule
        if not (0 <= ms_offset < 3600000):
            bad_ts += 1
        records.append((ts, bid, ask, bid_vol, ask_vol))

    df = None
    minute_rows = 0
    if records:
        tdf = pd.DataFrame(records, columns=['timestamp','bid','ask','bid_vol','ask_vol'])
        tdf['price'] = (tdf['bid'] + tdf['ask']) / 2.0
        tdf['volume'] = tdf['bid_vol'].fillna(0) + tdf['ask_vol'].fillna(0)
        tdf = tdf.set_index('timestamp')
        ohlc = tdf['price'].resample('1min').agg(['first','max','min','last'])
        volsum = tdf['volume'].resample('1min').sum()
        ohlc = ohlc.rename(columns={'first':'open','max':'high','min':'low','last':'close'})
        ohlc['volume'] = volsum
        ohlc = ohlc.dropna(subset=['open'])
        ohlc = ohlc.reset_index()
        minute_rows = len(ohlc)
        df = ohlc

    entry = {
        'file': fname,
        'decompress_attempts': {'lzma': 'ok'},
        'tick_count': len(records),
        'first_timestamp': str(records[0][0].to_pydatetime().isoformat()) if records else None,
        'last_timestamp': str(records[-1][0].to_pydatetime().isoformat()) if records else None,
        'validation_failures': {
            'bad_bid': bad_bid,
            'bad_ask': bad_ask,
            'bad_spread': bad_spread,
            'bad_ts': bad_ts,
        },
        'minute_rows': minute_rows,
        'pass': (bad_bid == 0 and bad_ask == 0 and bad_spread == 0 and bad_ts == 0)
    }

    results['files'].append(entry)
    results['hours_tested'] += 1
    if entry['pass']:
        results['hours_passed'] += 1
    else:
        results['hours_failed'] += 1

# overwrite artifact
ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
with open(ARTIFACT, 'w') as f:
    json.dump(results, f, indent=2)

print('Validation complete:', results['hours_tested'], 'tested,', results['hours_passed'], 'passed,', results['hours_failed'], 'failed')

if results['hours_failed'] == 0:
    exit(0)
else:
    exit(2)
