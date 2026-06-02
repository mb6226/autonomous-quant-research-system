import pandas as pd

from app.features.feature_factory import (
    FeatureFactory,
)

from app.targets.target_factory import (
    TargetFactory,
)

from app.models.random_forest_classifier import (
    RandomForestClassifierModel,
)
from app.research.metrics import (
    MetricsEngine,
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
    RandomForestClassifierModel()
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
