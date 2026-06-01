from dataclasses import dataclass


@dataclass
class Experiment:
    name: str
    market: str
    timeframe: str
    feature_set: str
    target: str
    model: str
