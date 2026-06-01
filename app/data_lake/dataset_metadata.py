from dataclasses import dataclass

@dataclass(slots=True)
class DatasetMetadata:

    symbol: str

    timeframe: str

    rows: int

    start_date: str

    end_date: str

    source: str
