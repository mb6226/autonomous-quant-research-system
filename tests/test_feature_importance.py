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

split = int(len(df) * 0.8)

X_train = X.iloc[:split]
y_train = y.iloc[:split]

model = (
    XGBoostClassifierModel()
    .train(
        X_train,
        y_train,
    )
)

importance = list(
    zip(
        features,
        model.feature_importances_,
    )
)

importance = sorted(
    importance,
    key=lambda x: x[1],
    reverse=True,
)

for name, score in importance[:20]:
    print(
        f"{name:30s} {score:.6f}"
    )
