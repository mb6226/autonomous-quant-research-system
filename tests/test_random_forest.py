import pandas as pd

from app.research.dataset_builder import (
    ResearchDatasetBuilder,
)

from app.models.random_forest_model import (
    RandomForestModel,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1d.parquet"
)

dataset = (
    ResearchDatasetBuilder()
    .build(df)
)

dataset = dataset.dropna()

features = [
    "ema20",
    "ema50",
    "ema200",
    "rsi14",
    "atr14",

    "return_1",
    "return_5",
    "return_10",
    "return_20",

    "roc_5",
    "roc_10",
    "roc_20",

    "ema20_distance",
    "ema50_distance",
    "ema200_distance",

    "rsi_momentum",

    "volatility_5",
    "volatility_10",
    "volatility_20",

    "atr_ratio",
    "high_low_ratio",

    "ema20_above_50",
    "ema50_above_200",
    "ema20_above_200",

    "ema20_slope",
    "ema50_slope",
    "ema200_slope",

    "bull_regime",
    "bear_regime",

    "high_vol_regime",
    "low_vol_regime",

    "trend_regime",
]

X = dataset[features]

y = dataset[
    "target_forward_return_5"
]

split = int(
    len(dataset) * 0.8
)

X_train = X.iloc[:split]
X_test = X.iloc[split:]

y_train = y.iloc[:split]
y_test = y.iloc[split:]

model = (
    RandomForestModel()
    .train(
        X_train,
        y_train,
    )
)

predictions = model.predict(
    X_test
)

print(
    "TRAIN ROWS =",
    len(X_train),
)

print(
    "TEST ROWS =",
    len(X_test),
)

print()

print(
    "FIRST 10 PREDICTIONS:"
)

print(
    predictions[:10]
)
