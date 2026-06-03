#!/usr/bin/env python3
"""Monthly gap-fill runner writing only to 1m_gapfill_test.parquet.

Monthly batches from START to END (inclusive). Resume support, dedupe, append.
Generates artifacts/eurusd_gapfill_progress.json and artifacts/eurusd_gapfill_summary.json
"""
from pathlib import Path
from datetime import datetime, timezone, date, timedelta
import calendar
import json
import struct
import lzma, zlib, bz2, gzip
import pandas as pd

import sys
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.providers.dukascopy.downloader import DukascopyDownloader


OUT_PARQUET = Path('data/raw/EURUSD/1m_gapfill_test.parquet')
ART_PROGRESS = Path('artifacts/eurusd_gapfill_progress.json')
ART_SUMMARY = Path('artifacts/eurusd_gapfill_summary.json')

START = date(2024,1,30)
END = date(2026,6,2)

duk = DukascopyDownloader(symbol='EURUSD')
session = duk.session

# If the test parquet already contains data beyond the configured START,
# advance START to the first day of the next month after the latest timestamp
# to avoid reprocessing fully-complete months and to resume from the next
# unprocessed month automatically.
try:
    if OUT_PARQUET.exists():
        _df_all = pd.read_parquet(OUT_PARQUET, columns=['timestamp'])
        if len(_df_all):
            _df_all['timestamp'] = pd.to_datetime(_df_all['timestamp'], utc=True)
            _last = _df_all['timestamp'].max()
            _ly, _lm = _last.year, _last.month
            if _lm == 12:
                _ny, _nm = _ly + 1, 1
            else:
                _ny, _nm = _ly, _lm + 1
            _next_month_start = date(_ny, _nm, 1)
            if _next_month_start > START:
                print('Adjusting START from', START, 'to', _next_month_start)
                START = _next_month_start
except Exception:
    pass

progress = []
checkpoints = {f"{y}-Q{q}": False for y in range(2024, 2027) for q in (1,2,3,4) if not (y==2026 and q>2)}
last_validation = None

def month_count_between(a, b):
    return (b.year - a.year) * 12 + (b.month - a.month) + 1

TOTAL_MONTHS = month_count_between(START, END)

def quarter_label(d):
    q = (d.month - 1)//3 + 1
    return f"{d.year}-Q{q}"

def month_iter(start_date, end_date):
    y, m = start_date.year, start_date.month
    while True:
        first = date(y, m, 1)
        last_day = calendar.monthrange(y, m)[1]
        last = date(y, m, last_day)
        ms = max(first, start_date)
        me = min(last, end_date)
        if ms <= me:
            yield (y, m, ms, me)
        if (y, m) == (end_date.year, end_date.month):
            break
        # increment month
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

for (y, m, month_start, month_end) in month_iter(START, END):
    month_label = f"{y:04d}-{m:02d}"
    hours_downloaded = 0
    files_downloaded = 0
    ticks_processed = 0
    minute_rows_generated = 0

    monthly_minutes = []

    # load existing timestamps to support resume/dedupe
    existing_ts = set()
    existing_month_df = None
    if OUT_PARQUET.exists():
        try:
            existing_df = pd.read_parquet(OUT_PARQUET)
            existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'], utc=True)
            mask = (existing_df['timestamp'].dt.date >= month_start) & (existing_df['timestamp'].dt.date <= month_end)
            existing_month_df = existing_df.loc[mask]
            existing_ts = set(existing_month_df['timestamp'].astype(str).tolist())
        except Exception:
            existing_ts = set()
            existing_month_df = None

    # Quick skip: if the target month is already fully present in OUT_PARQUET,
    # avoid downloading and mark the month with zero generated rows to prevent
    # false stall alerts and unnecessary work.
    try:
        if existing_month_df is not None:
            expected_minutes = int(((pd.Timestamp(month_end, tz='UTC') + pd.Timedelta(days=1)) - pd.Timestamp(month_start, tz='UTC')).total_seconds() / 60)
            if len(existing_month_df) >= expected_minutes:
                # month fully covered — add zeroed progress entry and continue
                hours_downloaded = 0
                files_downloaded = 0
                ticks_processed = 0
                minute_rows_generated = 0
                duplicates_removed = 0
                parquet_size_mb = OUT_PARQUET.stat().st_size / 1024 / 1024 if OUT_PARQUET.exists() else 0.0
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

                # update checkpoints for quarter completion (same logic as below)
                qlabel = quarter_label(month_end)
                if qlabel in checkpoints:
                    qnum = int(qlabel.split('-Q')[1])
                    q_last_month = qnum * 3
                    if month_end.month == q_last_month:
                        checkpoints[qlabel] = True

                ART_PROGRESS.parent.mkdir(parents=True, exist_ok=True)
                progress_payload = {
                    'progress': progress,
                    'checkpoints': checkpoints,
                    'last_validation': last_validation
                }
                with open(ART_PROGRESS, 'w') as f:
                    json.dump(progress_payload, f, indent=2)

                # print required per-month summary
                print('MONTH:', month_label)
                print('hours_downloaded', hours_downloaded)
                print('ticks_processed', ticks_processed)
                print('minute_rows_generated', minute_rows_generated)
                print('duplicates_removed', duplicates_removed)
                print('parquet_rows_total', parquet_rows_total)
                print('parquet_size_mb', round(parquet_size_mb,3))
                sys.stdout.flush()

                # run validation/early-quarter reporting as in main loop
                if len(progress) % 3 == 0:
                    try:
                        dfv = pd.read_parquet(OUT_PARQUET)
                        dfv['timestamp'] = pd.to_datetime(dfv['timestamp'], utc=True)
                        row_count = len(dfv)
                        start_ts = dfv['timestamp'].min().isoformat() if row_count>0 else None
                        end_ts = dfv['timestamp'].max().isoformat() if row_count>0 else None
                        dup_count = dfv['timestamp'].duplicated().sum()
                        last_validation = {
                            'checked_after_month': month_label,
                            'row_count': int(row_count),
                            'start_timestamp': start_ts,
                            'end_timestamp': end_ts,
                            'duplicate_timestamps': int(dup_count)
                        }
                        progress_payload['last_validation'] = last_validation
                        with open(ART_PROGRESS, 'w') as f:
                            json.dump(progress_payload, f, indent=2)
                        print('VALIDATION:', last_validation)
                        if row_count == 0 or dup_count > 0 or start_ts is None or end_ts is None:
                            print('Validation failed — stopping gap-fill as requested')
                            sys.exit(2)
                    except Exception as e:
                        print('Validation error — stopping gap-fill', e)
                        sys.exit(2)

                if checkpoints.get('2024-Q1') and not any(p.get('early_reported') for p in progress if p['month'].startswith('2024-01')):
                    q_rows = sum(p['minute_rows_generated'] for p in progress if p['month'].startswith('2024-0') or p['month'].startswith('2024-01') or p['month'].startswith('2024-02') or p['month'].startswith('2024-03'))
                    q_hours = sum(p['hours_downloaded'] for p in progress if p['month'].startswith('2024-0') or p['month'].startswith('2024-01') or p['month'].startswith('2024-02') or p['month'].startswith('2024-03'))
                    est_final_size_mb = round((parquet_size_mb or 0.0) * (TOTAL_MONTHS / max(1, len(progress))), 2)
                    early = {'quarter':'2024-Q1','rows_added':int(q_rows),'hours_downloaded':int(q_hours),'parquet_size_mb':round(parquet_size_mb,3),'estimated_final_size_mb':est_final_size_mb}
                    print('EARLY_QUARTER_REPORT:', early)
                    if progress:
                        progress[-1]['early_reported'] = True
                        progress_payload['progress'] = progress
                        with open(ART_PROGRESS, 'w') as f:
                            json.dump(progress_payload, f, indent=2)

                # skip actual downloads for this month
                continue
    except Exception:
        # if anything goes wrong in the skip-check, fall back to normal processing
        pass

    # determine resume point from existing parquet to avoid re-downloading already-covered hours
    last_ts_global = None
    if OUT_PARQUET.exists():
        try:
            all_existing = pd.read_parquet(OUT_PARQUET, columns=['timestamp'])
            all_existing['timestamp'] = pd.to_datetime(all_existing['timestamp'], utc=True)
            if len(all_existing):
                last_ts_global = all_existing['timestamp'].max().to_pydatetime()
        except Exception:
            last_ts_global = None

    # start day/hour: if last_ts_global falls inside or before this month, resume from that hour
    day = month_start
    start_hour_for_day = 0
    if last_ts_global is not None:
        try:
            if last_ts_global.date() >= month_start and last_ts_global.date() <= month_end:
                day = last_ts_global.date()
                start_hour_for_day = last_ts_global.hour
            elif last_ts_global.date() > month_end:
                # already have data beyond this month; skip month (handled by skip-check earlier)
                pass
        except Exception:
            day = month_start

    while day <= month_end:
        for hour in range(start_hour_for_day if (last_ts_global is not None and day == last_ts_global.date()) else 0, 24):
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
            # filter out minutes already present (resume)
            ohlc['ts_str'] = ohlc['timestamp'].astype(str)
            new_ohlc = ohlc[~ohlc['ts_str'].isin(existing_ts)].drop(columns=['ts_str'])
            minute_rows_generated += len(new_ohlc)
            if not new_ohlc.empty:
                monthly_minutes.append(new_ohlc)
            hours_downloaded += 1
        day = day + timedelta(days=1)

    if monthly_minutes:
        combined = pd.concat(monthly_minutes, ignore_index=True)
        before = 0
        try:
            if OUT_PARQUET.exists():
                old = pd.read_parquet(OUT_PARQUET)
                before = len(old)
                # concat and dedupe
                newall = pd.concat([old, combined], ignore_index=True)
            else:
                newall = combined
            newall['timestamp'] = pd.to_datetime(newall['timestamp'], utc=True)
            newall = newall.sort_values('timestamp').reset_index(drop=True)
            after = len(newall.drop_duplicates(subset=['timestamp'], keep='first'))
            newall = newall.drop_duplicates(subset=['timestamp'], keep='first')
            newall.to_parquet(OUT_PARQUET, index=False)
            parquet_size_mb = OUT_PARQUET.stat().st_size / 1024 / 1024
            duplicates_removed = before + len(combined) - after
        except Exception as e:
            print('Error writing parquet for', month_label, e)
            duplicates_removed = 0
            parquet_size_mb = OUT_PARQUET.stat().st_size / 1024 / 1024 if OUT_PARQUET.exists() else 0.0
    else:
        duplicates_removed = 0
        parquet_size_mb = OUT_PARQUET.stat().st_size / 1024 / 1024 if OUT_PARQUET.exists() else 0.0

    # compute parquet rows total after write
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
    # update checkpoints for quarter completion
    qlabel = quarter_label(month_end)
    if qlabel in checkpoints:
        # mark quarter completed if this month is the quarter's last month
        qnum = int(qlabel.split('-Q')[1])
        q_last_month = qnum * 3
        if month_end.month == q_last_month:
            checkpoints[qlabel] = True

    ART_PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    progress_payload = {
        'progress': progress,
        'checkpoints': checkpoints,
        'last_validation': last_validation
    }
    with open(ART_PROGRESS, 'w') as f:
        json.dump(progress_payload, f, indent=2)

    # print required per-month summary
    # print required per-month summary + parquet totals
    print('MONTH:', month_label)
    print('hours_downloaded', hours_downloaded)
    print('ticks_processed', ticks_processed)
    print('minute_rows_generated', minute_rows_generated)
    print('duplicates_removed', duplicates_removed)
    print('parquet_rows_total', parquet_rows_total)
    print('parquet_size_mb', round(parquet_size_mb,3))

    # flush to ensure visibility
    sys.stdout.flush()

    # Every 3 completed months, run validation checks
    if len(progress) % 3 == 0:
        try:
            dfv = pd.read_parquet(OUT_PARQUET)
            dfv['timestamp'] = pd.to_datetime(dfv['timestamp'], utc=True)
            row_count = len(dfv)
            start_ts = dfv['timestamp'].min().isoformat() if row_count>0 else None
            end_ts = dfv['timestamp'].max().isoformat() if row_count>0 else None
            dup_count = dfv['timestamp'].duplicated().sum()
            last_validation = {
                'checked_after_month': month_label,
                'row_count': int(row_count),
                'start_timestamp': start_ts,
                'end_timestamp': end_ts,
                'duplicate_timestamps': int(dup_count)
            }
            # update progress artifact with validation
            progress_payload['last_validation'] = last_validation
            with open(ART_PROGRESS, 'w') as f:
                json.dump(progress_payload, f, indent=2)
            print('VALIDATION:', last_validation)
            # if validation fails, stop immediately
            if row_count == 0 or dup_count > 0 or start_ts is None or end_ts is None:
                print('Validation failed — stopping gap-fill as requested')
                sys.exit(2)
        except Exception as e:
            print('Validation error — stopping gap-fill', e)
            sys.exit(2)

    # Early report when first full quarter completed (2024-Q1)
    if checkpoints.get('2024-Q1') and not any(p.get('early_reported') for p in progress if p['month'].startswith('2024-01')):
        # compute rows added and hours for Q1 2024
        q_rows = sum(p['minute_rows_generated'] for p in progress if p['month'].startswith('2024-0') or p['month'].startswith('2024-01') or p['month'].startswith('2024-02') or p['month'].startswith('2024-03'))
        q_hours = sum(p['hours_downloaded'] for p in progress if p['month'].startswith('2024-0') or p['month'].startswith('2024-01') or p['month'].startswith('2024-02') or p['month'].startswith('2024-03'))
        est_final_size_mb = round((parquet_size_mb or 0.0) * (TOTAL_MONTHS / max(1, len(progress))), 2)
        early = {'quarter':'2024-Q1','rows_added':int(q_rows),'hours_downloaded':int(q_hours),'parquet_size_mb':round(parquet_size_mb,3),'estimated_final_size_mb':est_final_size_mb}
        print('EARLY_QUARTER_REPORT:', early)
        # mark in progress entries to avoid repeating
        if progress:
            progress[-1]['early_reported'] = True
            progress_payload['progress'] = progress
            with open(ART_PROGRESS, 'w') as f:
                json.dump(progress_payload, f, indent=2)

# final summary
total_hours = sum(p['hours_downloaded'] for p in progress)
total_ticks = sum(p['ticks_processed'] for p in progress)
total_minutes = sum(p['minute_rows_generated'] for p in progress)
total_dup = sum(p['duplicates_removed'] for p in progress)

summary = {
    'start_date': START.isoformat(),
    'end_date': END.isoformat(),
    'months_processed': len(progress),
    'hours_downloaded': total_hours,
    'ticks_processed': total_ticks,
    'minute_rows_generated': total_minutes,
    'duplicates_removed': total_dup,
    'parquet_size_mb': round(OUT_PARQUET.stat().st_size / 1024 / 1024, 3) if OUT_PARQUET.exists() else 0.0
}
with open(ART_SUMMARY, 'w') as f:
    json.dump(summary, f, indent=2)

print('\nFINAL SUMMARY:')
print(summary)

# Validation: print rows, start_timestamp, end_timestamp for test parquet
if OUT_PARQUET.exists():
    df = pd.read_parquet(OUT_PARQUET)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    rows = len(df)
    s = df['timestamp'].min().isoformat() if rows>0 else None
    e = df['timestamp'].max().isoformat() if rows>0 else None
else:
    rows = 0; s = None; e = None

print('\nVALIDATION of', str(OUT_PARQUET))
print('rows', rows)
print('start_timestamp', s)
print('end_timestamp', e)

print('\nGap-fill test parquet complete. Stopping as requested.')
