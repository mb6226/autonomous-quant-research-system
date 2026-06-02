import pandas as pd

from app.features.feature_factory import (
    FeatureFactory,
)

from app.targets.target_factory import (
    TargetFactory,
)

from app.models.xgboost_classifier import (
    XGBoostClassifierModel,
)

from app.research.metrics import (
    MetricsEngine,
)

from sklearn.metrics import (
    confusion_matrix,
)

df = pd.read_parquet(
    "data/raw/US30/1d.parquet"
)

df = (
    FeatureFactory()
    .build(df)
)

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
    if str(df[c].dtype)
    in [
        "float64",
        "int64",
        "bool",
    ]
]

if "target" in features:
    features.remove("target")

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
    XGBoostClassifierModel()
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
import pandas as pd

from app.features.feature_factory import (
    FeatureFactory,
)

from app.targets.target_factory import (
    TargetFactory,
)

from app.models.xgboost_classifier import (
    XGBoostClassifierModel,
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

df = (
    FeatureFactory()
    .build(df)
)

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
    if str(df[c].dtype)
    in [
        "float64",
        "int64",
        "bool",
    ]
]

if "target" in features:
    features.remove("target")

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
    XGBoostClassifierModel()
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
