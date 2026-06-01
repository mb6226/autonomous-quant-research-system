from dataclasses import dataclass

@dataclass(slots=True)
class DownloadJob:

    symbol: str

    timeframe: str

    start_date: str

    end_date: str

    provider: str
