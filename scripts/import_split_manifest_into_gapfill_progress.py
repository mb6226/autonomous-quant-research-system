#!/usr/bin/env python3
"""Import `artifacts/eurusd_split_manifest.json` into the gapfill progress manifest.

This creates/updates `artifacts/eurusd_gapfill_progress.json` with checkpoints
for months already present as chunk files so the gapfill runner will skip them.
"""
from pathlib import Path
import json
from datetime import datetime, timezone

SPLIT_MANIFEST = Path('artifacts/eurusd_split_manifest.json')
PROGRESS = Path('artifacts/eurusd_gapfill_progress.json')

def main():
    if not SPLIT_MANIFEST.exists():
        print('Split manifest not found:', SPLIT_MANIFEST)
        return 2
    split = json.loads(SPLIT_MANIFEST.read_text())
    chunks = split.get('chunks', {})

    progress = []
    checkpoints = {}
    now = datetime.now(timezone.utc).isoformat()
    cumulative = 0
    for month in sorted(chunks.keys()):
        info = chunks[month]
        file = info.get('file')
        rows = int(info.get('rows', 0))
        cumulative += rows
        entry = {
            'month': month,
            'month_start': info.get('start_timestamp'),
            'month_end': info.get('end_timestamp'),
            'hours_downloaded': None,
            'files_downloaded': None,
            'ticks_processed': None,
            'minute_rows_generated': rows,
            'duplicates_removed': 0,
            'parquet_size_mb': None,
            'parquet_rows_total': cumulative
        }
        progress.append(entry)
        checkpoints[month] = {
            'file': file,
            'rows': rows,
            'duplicates_removed': 0,
            'status': 'done',
            'completed_at': now
        }

    payload = {'progress': progress, 'checkpoints': checkpoints, 'last_validation': None}
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text(json.dumps(payload, indent=2))
    print('Wrote', PROGRESS)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
