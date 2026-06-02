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

model = (
    XGBoostClassifierModel()
    .train(
        X.iloc[:split],
        y.iloc[:split],
    )
)

ranking = sorted(
    zip(
        features,
        model.feature_importances_,
    ),
    key=lambda x: x[1],
    reverse=True,
)

print()
print("TOP 10 FEATURES")
print()

for i, (name, score) in enumerate(
    ranking[:10],
    start=1,
):
    print(
        f"{i:2d}. {name:30s} {score:.6f}"
    )
