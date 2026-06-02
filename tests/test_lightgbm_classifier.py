import pandas as pd

from app.features.feature_factory import (
    FeatureFactory,
)

from app.targets.target_factory import (
    TargetFactory,
)

from app.models.lightgbm_classifier import (
    LightGBMClassifierModel,
)

from app.research.metrics import (
    MetricsEngine,
)

from sklearn.metrics import (
    confusion_matrix,
)

df = pd.read_parquet(
    "data/raw/BTCUSDT/1d.parquet"
)

df = FeatureFactory().build(df)

df["target"] = (
    TargetFactory()
    .classification_up_down(
        df,
        periods=5,
    )
)

df = df.dropna()

features = [
    c
    for c in df.columns
    if c not in [
        "timestamp",
        "target",
        "ignore",
        "open_time",
        "close_time",
    ]
]

X = df[features]
y = df["target"]

split = int(
    len(df) * 0.8
)

X_train = X.iloc[:split]
X_test = X.iloc[split:]

y_train = y.iloc[:split]
y_test = y.iloc[split:]

model = (
    LightGBMClassifierModel()
    .train(
        X_train,
        y_train,
    )
)

pred = model.predict(
    X_test
)

metrics = (
    MetricsEngine()
    .classification_metrics(
        y_test,
        pred,
    )
)

print()
print("TRAIN =", len(X_train))
print("TEST =", len(X_test))
print()

print(metrics)
print()

print(
    confusion_matrix(
        y_test,
        pred,
    )
)
