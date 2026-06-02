import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

from app.data.jobs.download_job import DownloadJob
from app.data.providers.binance.provider import BinanceProvider
from app.data.providers.yahoo.provider import YahooProvider

MANIFEST_DIR = Path.cwd() / "data" / "manifests"
RAW_DIR = Path.cwd() / "data" / "raw"
ARTIFACTS_DIR = Path.cwd() / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)


def read_manifest(market: str, timeframe: str):
    path = MANIFEST_DIR / f"{market}_{timeframe}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def write_manifest(market: str, timeframe: str, rows: int, start: str, end: str):
    path = MANIFEST_DIR / f"{market}_{timeframe}.json"
    data = {
        "symbol": market,
        "timeframe": timeframe,
        "rows": rows,
        "start": start,
        "end": end,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def parquet_path(market: str, timeframe: str) -> Path:
    d = RAW_DIR / market
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{timeframe}.parquet"


def load_existing(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def to_iso(dt: datetime) -> str:
    return dt.isoformat()


def run_acquisition(tasks):
    status = []
    now = datetime.utcnow()
    for task in tasks:
        market = task["market"]
        timeframe = task["timeframe"]
        provider_name = task.get("provider")

        out = parquet_path(market, timeframe)
        existing = load_existing(out)

        manifest = read_manifest(market, timeframe)

        if existing.empty and manifest:
            # nothing in raw but manifest exists — set start from manifest
            start_date = manifest.get("start")
        elif not existing.empty:
            # resume from last timestamp
            last_ts = pd.to_datetime(existing["timestamp"]).max()
            # advance by one interval
            start_date = (last_ts + timedelta(seconds=1)).isoformat()
        else:
            # no data — set a default start (2 years ago)
            start_date = (now - timedelta(days=365 * 2)).isoformat()

        end_date = now.isoformat()

        job = DownloadJob(
            symbol=market,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            provider=provider_name,
        )

        try:
            if provider_name == "binance":
                prov = BinanceProvider()
                df = prov.download(job)
            else:
                prov = YahooProvider()
                interval = timeframe if timeframe.endswith("d") else timeframe
                df = prov.download_history(job.symbol + "=X" if job.symbol.isalpha() else job.symbol, start_date, end_date, interval=job.timeframe)

            if df is None or df.empty:
                status.append({"market": market, "timeframe": timeframe, "rows": 0, "start_date": start_date, "end_date": end_date, "status": "no_data"})
                continue

            # standardize timestamp column
            if "timestamp" not in df.columns and "ts" in df.columns:
                df = df.rename(columns={"ts": "timestamp"})

            if "timestamp" not in df.columns:
                # try to infer
                if "open_time" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)

            # merge with existing and dedupe
            if not existing.empty:
                combined = pd.concat([existing, df], ignore_index=True)
            else:
                combined = df

            if "timestamp" in combined.columns:
                combined = combined.drop_duplicates(subset=["timestamp"]).sort_values(by="timestamp").reset_index(drop=True)

            # write parquet
            combined.to_parquet(out, index=False)

            rows = len(combined)
            start = combined["timestamp"].min().isoformat() if "timestamp" in combined.columns else start_date
            end = combined["timestamp"].max().isoformat() if "timestamp" in combined.columns else end_date

            write_manifest(market, timeframe, rows, start, end)

            status.append({"market": market, "timeframe": timeframe, "rows": rows, "start_date": start, "end_date": end, "status": "ok"})

        except Exception as e:
            status.append({"market": market, "timeframe": timeframe, "rows": 0, "start_date": start_date, "end_date": end_date, "status": f"error: {e}"})

    out_path = ARTIFACTS_DIR / "acquisition_status.json"
    with open(out_path, "w") as f:
        json.dump({"results": status}, f, indent=2)

    print(f"Wrote acquisition status: {out_path}")


if __name__ == "__main__":
    tasks = [
        {"market": "BTCUSDT", "timeframe": "30m", "provider": "binance"},
        {"market": "BTCUSDT", "timeframe": "15m", "provider": "binance"},
        {"market": "EURUSD", "timeframe": "30m", "provider": "yahoo"},
        {"market": "EURUSD", "timeframe": "15m", "provider": "yahoo"},
    ]
    run_acquisition(tasks)
