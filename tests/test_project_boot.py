from app.core.experiment import (
    Experiment,
)

experiment = Experiment(
    symbol="BTCUSDT",
    timeframe="1h",
    features=[],
    model="rf",
    target="direction",
)

print(experiment)
