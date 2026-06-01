from dataclasses import dataclass

@dataclass(slots=True)
class DatasetManifest:

    symbol: str

    timeframe: str

    provider: str

    start_date: str

    end_date: str

    path: str

    rows: int
