from dataclasses import dataclass

@dataclass(slots=True)
class ExperimentResult:

    symbol: str

    timeframe: str

    model: str

    target: str

    accuracy: float

    win_rate: float

    profit_factor: float

    pnl: float
