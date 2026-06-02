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

results = []

for removed in features[:15]:

    current = [
        f
        for f in features
        if f != removed
    ]

    X = df[current]
    y = df["target"]

    split = int(
        len(df) * 0.8
    )

    model = (
        XGBoostClassifierModel()
        .train(
            X.iloc[:split],
            y.iloc[:split],
        )
    )

    pred = model.predict(
        X.iloc[split:]
    )

    metrics = (
        MetricsEngine()
        .classification_metrics(
            y.iloc[split:],
            pred,
        )
    )

    results.append(
        (
            removed,
            metrics["accuracy"],
        )
    )

results = sorted(
    results,
    key=lambda x: x[1],
)

print()
print("ABLATION RESULTS")
print()

for row in results:
    print(row)
