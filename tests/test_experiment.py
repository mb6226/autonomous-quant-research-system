from app.research.experiment import (
    Experiment,
)

exp = Experiment(
    name="btc_rf_v1",
    market="BTCUSDT",
    timeframe="1d",
    feature_set="baseline",
    target="forward_return_5",
    model="random_forest",
)

print(exp)
