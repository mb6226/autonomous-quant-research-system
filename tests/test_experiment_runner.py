import pandas as pd

from app.core.experiment import (
    Experiment,
)

from app.research.experiment_runner import (
    ExperimentRunner,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1d.parquet"
)

experiment = Experiment(
    name="btc_rf_v1",
    market="BTCUSDT",
    timeframe="1d",
    feature_set="baseline",
    target="forward_return_5",
    model="random_forest",
)

result = (
    ExperimentRunner()
    .run(
        experiment,
        df,
    )
)

print(result)
