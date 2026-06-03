import os
import json
import time
import requests
import pandas as pd
import pyarrow
import lzma
import bz2
import zlib
import gzip
import io

from pathlib import Path
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class DukascopyDownloader:

    BASE_URL = "https://datafeed.dukascopy.com/datafeed"

    def __init__(self, symbol: str = "EURUSD"):

        self.symbol = symbol

        self.output_dir = Path("data") / "raw" / self.symbol

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=(502, 503, 504))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _hour_url(self, year: int, month: int, day: int, hour: int) -> str:
        # Dukascopy hourly ticks file pattern (common public pattern)
        # e.g. /datafeed/EURUSD/2018/01/01/00h_ticks.bi5
        return f"{self.BASE_URL}/{self.symbol}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"

    def download_hour(self, year: int, month: int, day: int, hour: int) -> pd.DataFrame:
        url = self._hour_url(year, month, day, hour)
        try:
            r = self.session.get(url, timeout=30)
            if r.status_code != 200:
                print(f"No hour data: {url} -> {r.status_code}")
                return pd.DataFrame()
            content = r.content
            # Dukascopy hourly files are usually .bi5 compressed binary of ticks; parsing requires specialized logic.
            # Try: plain text CSV, then multiple decompressors (lzma, zlib, bz2, gzip) and CSV parse.
            attempts = []

            def try_parse_bytes(b: bytes):
                try:
                    txt = b.decode("utf-8")
                    df = pd.read_csv(pd.io.common.StringIO(txt))
                    return df
                except Exception:
                    return None

            # 1) try raw bytes as UTF-8 CSV
            df = try_parse_bytes(content)
            if df is not None:
                print(f"Parsed hour as CSV (raw) {year}-{month:02d}-{day:02d} {hour:02d}")
                return df

            # 2) try lzma
            for name, func in (
                ("lzma", lambda b: lzma.decompress(b)),
                ("zlib", lambda b: zlib.decompress(b)),
                ("bz2", lambda b: bz2.decompress(b)),
                ("gzip", lambda b: gzip.decompress(b)),
            ):
                try:
                    out = func(content)
                    # if decompressed bytes are text CSV, parse
                    df = try_parse_bytes(out)
                    if df is not None:
                        print(f"Parsed hour as CSV after {name} decompress {year}-{month:02d}-{day:02d} {hour:02d}")
                        return df

                    # If decompressed bytes appear to be binary ticks (length divisible by 20),
                    # parse 20-byte records: >qiii (big-endian int64, int32, int32, int32)
                    if len(out) % 20 == 0 and len(out) >= 20:
                        import struct
                        records = []
                        for i in range(0, len(out), 20):
                            chunk = out[i : i + 20]
                            try:
                                ts_ms, a, b, vol = struct.unpack('>qiii', chunk)
                            except struct.error:
                                # fall back to unsigned ints if signed fails
                                ts_ms = struct.unpack('>q', chunk[:8])[0]
                                a = int.from_bytes(chunk[8:12], 'big', signed=False)
                                b = int.from_bytes(chunk[12:16], 'big', signed=False)
                                vol = int.from_bytes(chunk[16:20], 'big', signed=False)
                            # compute mid price
                            price = (a + b) / 2.0 / 100000.0
                            ts = pd.to_datetime(ts_ms, unit='ms', utc=True)
                            records.append((ts, price, vol))

                        if records:
                            tdf = pd.DataFrame(records, columns=['timestamp', 'price', 'volume'])
                            # aggregate to 1m OHLCV
                            tdf = tdf.set_index('timestamp')
                            # use explicit minute alias to be compatible across pandas versions
                            ohlc = tdf['price'].resample('1min').agg(['first','max','min','last'])
                            volsum = tdf['volume'].resample('1T').sum()
                            volsum = tdf['volume'].resample('1min').sum()
                            ohlc = ohlc.rename(columns={'first':'open','max':'high','min':'low','last':'close'})
                            ohlc['volume'] = volsum
                            ohlc = ohlc.dropna(subset=['open'])
                            ohlc = ohlc.reset_index()
                            print(f"Parsed hour as binary ticks->{len(ohlc)} bars after {name} decompress {year}-{month:02d}-{day:02d} {hour:02d}")
                            return ohlc

                    attempts.append((name, "decompressed but not CSV or binary-ticks"))
                except Exception as e:
                    attempts.append((name, f"decompress failed: {e}"))

            # If we reach here, we could not parse. Save raw content for inspection.
            debug_dir = self.output_dir / "dukascopy_debug"
            debug_dir.mkdir(parents=True, exist_ok=True)
            out_path = debug_dir / f"{year:04d}-{month:02d}-{day:02d}-{hour:02d}.bin"
            try:
                with open(out_path, "wb") as f:
                    f.write(content)
                print(f"Saved unparseable hour to {out_path}; attempts: {attempts}")
            except Exception as e:
                print(f"Failed to save debug file {out_path}: {e}; attempts: {attempts}")
            return pd.DataFrame()

        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return pd.DataFrame()

    def download_day(self, year: int, month: int, day: int) -> pd.DataFrame:
        parts = []
        for hour in range(24):
            df_h = self.download_hour(year, month, day, hour)
            if not df_h.empty:
                parts.append(df_h)
            time.sleep(0.1)

        if not parts:
            return pd.DataFrame()

        df = pd.concat(parts, ignore_index=True)
        return df

    def download_month(self, year: int, month: int) -> pd.DataFrame:
        print(f"Downloading month {year}-{month:02d} for {self.symbol}")
        parts = []
        # estimate days in month
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)

        day = start
        while day < end:
            try:
                df_day = self.download_day(day.year, day.month, day.day)
                if not df_day.empty:
                    parts.append(df_day)
            except Exception as e:
                print(f"Failed day {day.date()}: {e}")
            day = day + timedelta(days=1)

        if not parts:
            return pd.DataFrame()

        month_df = pd.concat(parts, ignore_index=True)
        return month_df

    def download_range(self, start_year: int, end_year: int):
        # iterate months and save incrementally
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                try:
                    df = self.download_month(year, month)
                    if df.empty:
                        continue

                    self.save_parquet(df)
                    self.update_manifest()
                except Exception as e:
                    print(f"Failed month {year}-{month:02d}: {e}")

    def save_parquet(self, df: pd.DataFrame) -> Path:
        path = (
            self.output_dir / "1m.parquet"
        )

        if df.empty:
            return path

        # normalize timestamp column
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        if path.exists():
            try:
                old = pd.read_parquet(path)
                combined = pd.concat([old, df], ignore_index=True)
            except Exception:
                combined = df
        else:
            combined = df

        if "timestamp" in combined.columns:
            combined = (
                combined.drop_duplicates(subset=["timestamp"]) .sort_values("timestamp").reset_index(drop=True)
            )

        combined.to_parquet(path, index=False)
        print(f"Wrote parquet: {path} ({len(combined)} rows)")
        return path

    def update_manifest(self):
        path = self.output_dir / "1m.parquet"
        manifest_dir = Path.cwd() / "data" / "manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / f"{self.symbol}_1m.json"

        if not path.exists():
            print("No parquet to manifest")
            return

        try:
            df = pd.read_parquet(path)
            start = df["timestamp"].min().isoformat()
            end = df["timestamp"].max().isoformat()
            rows = len(df)
            manifest = {
                "symbol": self.symbol,
                "timeframe": "1m",
                "rows": rows,
                "start": start,
                "end": end,
            }
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            print(f"Wrote manifest: {manifest_path}")
        except Exception as e:
            print(f"Failed to update manifest: {e}")
