#!/usr/bin/env python3
"""Dukascopy gap-fill runner (new job)

Downloads EURUSD 1m data from 2025-05-01 to 2026-06-01 (UTC) into the test
parquet `data/raw/EURUSD/1m_gapfill_test.parquet` using monthly batches.

Requirements implemented:
- Resume support
- Monthly batching
- Dedupe on timestamp
- Writes artifacts/eurusd_gapfill_progress.json and artifacts/eurusd_gapfill_summary.json
- Stops on validation failure

DO NOT run if you don't want background downloads. This script is intended to be
started under the project's venv and can be run in foreground for debugging.
"""
from pathlib import Path
from datetime import datetime, timezone, date, timedelta
import calendar
import json
import struct
import lzma, zlib, bz2, gzip
import pandas as pd
import sys, os, time

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.providers.dukascopy.downloader import DukascopyDownloader

OUT_PARQUET = Path('data/raw/EURUSD/1m_gapfill_test.parquet')
ART_PROGRESS = Path('artifacts/eurusd_gapfill_progress.json')
ART_SUMMARY = Path('artifacts/eurusd_gapfill_summary.json')

# User-specified range
START_DATE = date(2025,5,1)
END_DATE = date(2026,6,1)  # exclusive end-day upper bound (we treat by month)

def month_count_between(a, b):
    return (b.year - a.year) * 12 + (b.month - a.month) + 1

TOTAL_MONTHS = month_count_between(START_DATE, (END_DATE - timedelta(days=1)))

def month_iter(start_date, end_date):
    y, m = start_date.year, start_date.month
    while True:
        first = date(y, m, 1)
        last_day = calendar.monthrange(y, m)[1]
        last = date(y, m, last_day)
        ms = max(first, start_date)
        me = min(last, end_date - timedelta(days=0))
        if ms <= me:
            yield (y, m, ms, me)
        if (y, m) == (end_date - timedelta(days=1)).timetuple()[:2]:
            break
        if m == 12:
            y += 1; m = 1
        else:
            m += 1

def decompress_content(content):
    for fn in (lzma.decompress, zlib.decompress, bz2.decompress, gzip.decompress):
        try:
            return fn(content)
        except Exception:
            continue
    return None

SCALE = 100000.0
FMT = '>IIIff'

def load_existing_timestamps_for_month(month_start, month_end):
    existing_ts = set()
    if OUT_PARQUET.exists():
        try:
            existing_df = pd.read_parquet(OUT_PARQUET, columns=['timestamp'])
            existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'], utc=True)
            mask = (existing_df['timestamp'].dt.date >= month_start) & (existing_df['timestamp'].dt.date <= month_end)
            existing_ts = set(existing_df.loc[mask, 'timestamp'].astype(str).tolist())
        except Exception:
            existing_ts = set()
    return existing_ts

def write_progress(progress, checkpoints, last_validation):
    ART_PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    payload = {'progress': progress, 'checkpoints': checkpoints, 'last_validation': last_validation}
    with open(ART_PROGRESS, 'w') as f:
        json.dump(payload, f, indent=2)

def run():
    duk = DukascopyDownloader(symbol='EURUSD')
    session = duk.session

    # print startup summary
    main_parquet = Path('data/raw/EURUSD/1m.parquet')
    if main_parquet.exists():
        try:
            md = pd.read_parquet(main_parquet, columns=['timestamp'])
            md['timestamp'] = pd.to_datetime(md['timestamp'], utc=True)
            current_end = md['timestamp'].max()
        except Exception:
            current_end = None
    else:
        current_end = None

    expected_months = month_count_between(START_DATE, END_DATE - timedelta(days=1))
    print('CURRENT_END_TIMESTAMP', str(current_end))
    print('START_DATE', START_DATE.isoformat())
    print('END_DATE', END_DATE.isoformat())
    print('EXPECTED_MONTHS', expected_months)

    pid = os.getpid()
    print('PID', pid)

    progress = []
    checkpoints = {}
    last_validation = None
    first_month_reported = None
    first_successful_hour = None

    for (y, m, month_start, month_end) in month_iter(START_DATE, END_DATE):
        month_label = f"{y:04d}-{m:02d}"
        if first_month_reported is None:
            first_month_reported = month_label
        hours_downloaded = 0
        files_downloaded = 0
        ticks_processed = 0
        minute_rows_generated = 0
        monthly_minutes = []

        existing_ts = load_existing_timestamps_for_month(month_start, month_end)

        day = month_start
        while day <= month_end:
            for hour in range(24):
                url = duk._hour_url(day.year, day.month, day.day, hour)
                try:
                    r = session.get(url, timeout=30)
                except Exception:
                    continue
                if r.status_code != 200:
                    continue
                files_downloaded += 1
                content = r.content
                dec = decompress_content(content)
                if dec is None or len(dec) < 20:
                    continue
                ticks = []
                for i in range(0, len(dec)//20 * 20, 20):
                    chunk = dec[i:i+20]
                    try:
                        ms_from_hour, ask_u, bid_u, ask_vol, bid_vol = struct.unpack(FMT, chunk)
                    except struct.error:
                        continue
                    ticks.append((int(ms_from_hour), int(ask_u), int(bid_u), float(ask_vol), float(bid_vol)))
                tick_count = len(ticks)
                ticks_processed += tick_count
                if tick_count == 0:
                    continue
                hour_start = pd.to_datetime(datetime(day.year, day.month, day.day, hour, tzinfo=timezone.utc))
                rows = []
                for (ms, ask_u, bid_u, ask_vol, bid_vol) in ticks:
                    ts = hour_start + pd.to_timedelta(ms, unit='ms')
                    ask = ask_u / SCALE
                    bid = bid_u / SCALE
                    price = (bid + ask) / 2.0
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
                ohlc['ts_str'] = ohlc['timestamp'].astype(str)
                new_ohlc = ohlc[~ohlc['ts_str'].isin(existing_ts)].drop(columns=['ts_str'])
                minute_rows_generated += len(new_ohlc)
                if not new_ohlc.empty:
                    monthly_minutes.append(new_ohlc)
                    if first_successful_hour is None:
                        first_successful_hour = hour_start.isoformat()
                hours_downloaded += 1
            day = day + timedelta(days=1)

        # write month combine
        parquet_size_mb = OUT_PARQUET.stat().st_size / 1024 / 1024 if OUT_PARQUET.exists() else 0.0
        if monthly_minutes:
            combined = pd.concat(monthly_minutes, ignore_index=True)
            try:
                if OUT_PARQUET.exists():
                    old = pd.read_parquet(OUT_PARQUET)
                    newall = pd.concat([old, combined], ignore_index=True)
                else:
                    newall = combined
                newall['timestamp'] = pd.to_datetime(newall['timestamp'], utc=True)
                newall = newall.sort_values('timestamp').reset_index(drop=True)
                newall = newall.drop_duplicates(subset=['timestamp'], keep='first')
                newall.to_parquet(OUT_PARQUET, index=False)
                parquet_size_mb = OUT_PARQUET.stat().st_size / 1024 / 1024
                duplicates_removed = 0
            except Exception as e:
                print('Error writing parquet for', month_label, e)
                duplicates_removed = 0
        else:
            duplicates_removed = 0

        try:
            parquet_rows_total = len(pd.read_parquet(OUT_PARQUET)) if OUT_PARQUET.exists() else 0
        except Exception:
            parquet_rows_total = 0

        entry = {
            'month': month_label,
            'month_start': month_start.isoformat(),
            'month_end': month_end.isoformat(),
            'hours_downloaded': hours_downloaded,
            'files_downloaded': files_downloaded,
            'ticks_processed': ticks_processed,
            'minute_rows_generated': minute_rows_generated,
            'duplicates_removed': duplicates_removed,
            'parquet_size_mb': round(parquet_size_mb,3),
            'parquet_rows_total': parquet_rows_total
        }
        progress.append(entry)
        write_progress(progress, checkpoints, last_validation)

        # print per-month summary
        print('MONTH:', month_label)
        print('hours_downloaded', hours_downloaded)
        print('ticks_processed', ticks_processed)
        print('minute_rows_generated', minute_rows_generated)
        print('parquet_rows_total', parquet_rows_total)
        sys.stdout.flush()

        # simple validation after each month
        try:
            dfv = pd.read_parquet(OUT_PARQUET)
            dfv['timestamp'] = pd.to_datetime(dfv['timestamp'], utc=True)
            row_count = len(dfv)
            dup_count = dfv['timestamp'].duplicated().sum()
            if row_count == 0 or dup_count > 0:
                print('Validation failed — stopping gap-fill')
                sys.exit(2)
        except Exception as e:
            print('Validation error — stopping gap-fill', e)
            sys.exit(2)

    # final summary
    try:
        final_df = pd.read_parquet(OUT_PARQUET)
        final_df['timestamp'] = pd.to_datetime(final_df['timestamp'], utc=True)
        rows = len(final_df)
        end_ts = final_df['timestamp'].max().isoformat() if rows>0 else None
    except Exception:
        rows = 0; end_ts = None

    summary = {
        'start_date': START_DATE.isoformat(),
        'end_date': END_DATE.isoformat(),
        'months_processed': len(progress),
        'parquet_rows_total': rows,
        'parquet_end_timestamp': end_ts
    }
    with open(ART_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2)

    print('\nFINAL SUMMARY:')
    print(summary)

    # after completion, run merge script as requested
    try:
        print('Running merge_gapfill_to_main.py')
        os.system('.venv/bin/python scripts/merge_gapfill_to_main.py')
    except Exception as e:
        print('Failed to run merge script:', e)

if __name__ == '__main__':
    run()
