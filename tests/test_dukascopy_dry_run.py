import json
from pathlib import Path


def test_dukascopy_dry_run_report_exists_and_valid():
    rpt = Path('artifacts/dukascopy_dry_run_report.json')
    assert rpt.exists(), 'Dry-run report not found: artifacts/dukascopy_dry_run_report.json'
    data = json.loads(rpt.read_text())
    keys = ['hours_downloaded', 'files_downloaded', 'ticks_processed', 'minute_rows_generated', 'duplicates_removed', 'start_timestamp', 'end_timestamp', 'parquet_size_mb']
    for k in keys:
        assert k in data, f'Missing key in report: {k}'
    assert data['hours_downloaded'] >= 1


def test_parquet_test_file_present():
    p = Path('data/raw/EURUSD/1m_gapfill_test.parquet')
    assert p.exists(), 'Test parquet not found: data/raw/EURUSD/1m_gapfill_test.parquet'
