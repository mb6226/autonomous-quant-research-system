from dataclasses import dataclass


@dataclass
class ExperimentResult:
    experiment_name: str

    rows: int

    sharpe: float

    sortino: float

    max_drawdown: float
