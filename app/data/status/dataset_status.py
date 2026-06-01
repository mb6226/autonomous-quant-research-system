from dataclasses import dataclass

@dataclass(slots=True)
class DatasetStatus:

    symbol: str

    timeframe: str

    provider: str

    downloaded_rows: int

    last_timestamp: int
