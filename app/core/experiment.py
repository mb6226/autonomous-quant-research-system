from dataclasses import dataclass

@dataclass(slots=True)
class Experiment:

    symbol: str

    timeframe: str

    features: list[str]

    model: str

    target: str
