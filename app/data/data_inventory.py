"""Scan dataset manifests and produce a coverage report.

Writes: artifacts/data_coverage_report.json

Usage: python -m app.data.data_inventory
"""
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Dict

MANIFEST_DIR = Path.cwd() / "data" / "manifests"
ARTIFACTS_DIR = Path.cwd() / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def parse_date(s: str) -> datetime:
    # Try flexible parsing for manifest date strings
    try:
        return datetime.fromisoformat(s)
    except Exception:
        try:
            return datetime.fromisoformat(s.replace(" ", "T"))
        except Exception:
            # Fallback: naive parse without timezone
            return datetime.strptime(s.split("+")[0].strip(), "%Y-%m-%d %H:%M:%S")


def timeframe_delta(timeframe: str) -> timedelta:
    # Map common timeframe tokens to timedeltas (approximate for months/year omitted)
    if timeframe.endswith("m") and timeframe[:-1].isdigit():
        minutes = int(timeframe[:-1])
        return timedelta(minutes=minutes)
    if timeframe.endswith("h") and timeframe[:-1].isdigit():
        hours = int(timeframe[:-1])
        return timedelta(hours=hours)
    if timeframe.endswith("d") and timeframe[:-1].isdigit():
        days = int(timeframe[:-1])
        return timedelta(days=days)
    # default daily
    return timedelta(days=1)


def build_report() -> Dict:
    report = []
    manifests = sorted(MANIFEST_DIR.glob("*.json"))
    for mf in manifests:
        try:
            with open(mf, "r") as f:
                data = json.load(f)
        except Exception:
            continue

        symbol = data.get("symbol") or data.get("market") or mf.stem.split("_")[0]
        timeframe = data.get("timeframe") or mf.stem.split("_")[-1]
        rows = int(data.get("rows", 0))
        start_s = data.get("start")
        end_s = data.get("end")
        start_date = None
        end_date = None
        missing_values = None
        if start_s and end_s:
            try:
                start_dt = parse_date(start_s)
                end_dt = parse_date(end_s)
                start_date = start_dt.isoformat()
                end_date = end_dt.isoformat()
                delta = timeframe_delta(timeframe)
                # inclusive count
                expected = int((end_dt - start_dt) / delta) + 1
                missing = max(0, expected - rows)
                missing_values = missing
            except Exception:
                start_date = start_s
                end_date = end_s

        report.append(
            {
                "market": symbol,
                "timeframe": timeframe,
                "rows": rows,
                "start_date": start_date,
                "end_date": end_date,
                "missing_values": missing_values,
            }
        )

    return {"datasets": report}


def write_artifact(path: Path, data: Dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def main():
    report = build_report()
    out = ARTIFACTS_DIR / "data_coverage_report.json"
    write_artifact(out, report)
    print(f"Wrote data coverage report: {out}")


if __name__ == "__main__":
    main()
