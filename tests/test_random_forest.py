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
