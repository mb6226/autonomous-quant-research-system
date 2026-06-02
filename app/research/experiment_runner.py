from dataclasses import dataclass
from typing import Any
import pandas as pd

from app.data.factory.dataset_factory import DatasetFactory
from app.features.feature_factory import FeatureFactory
from app.targets.target_factory import TargetFactory
from app.research.experiment_generator import Experiment as ExpType
from app.research.metrics import MetricsEngine


@dataclass
class ExperimentResultSimple:
    market: str
    timeframe: str
    model: str
    target: str
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    rows: int | None = None


class ExperimentRunner:

    def __init__(self, allow_sampling: bool = False):
        self.dataset_factory = DatasetFactory()
        self.feature_factory = FeatureFactory()
        self.target_factory = TargetFactory()
        self.metrics = MetricsEngine()
        self.allow_sampling = bool(allow_sampling)

    def _load_dataset(self, market: str, timeframe: str) -> pd.DataFrame:
        path = f"data/raw/{market}/{timeframe}.parquet"
        df = pd.read_parquet(path)
        return df

    def _get_model_impl(self, model_name: str) -> Any:
        # minimal mapping - extendable
        if model_name == "xgboost":
            from app.models.xgboost_classifier import XGBoostClassifierModel

            return XGBoostClassifierModel()
        if model_name == "random_forest":
            from app.models.random_forest_classifier import RandomForestClassifierModel

            return RandomForestClassifierModel()
        if model_name == "extra_trees":
            from app.models.extra_trees_classifier import ExtraTreesClassifierModel

            return ExtraTreesClassifierModel()
        if model_name == "lightgbm":
            from app.models.lightgbm_classifier import LightGBMClassifierModel

            return LightGBMClassifierModel()
        if model_name == "catboost":
            from app.models.catboost_classifier import CatBoostClassifierModel

            return CatBoostClassifierModel()
        raise ValueError(f"unsupported model: {model_name}")

    def _parse_target(self, df: pd.DataFrame, target_spec: str) -> pd.Series:
        # expected formats: classification_up_down_5, forward_return_1, volatility_10
        if target_spec.startswith("classification_up_down"):
            parts = target_spec.split("_")
            periods = int(parts[-1]) if parts[-1].isdigit() else 1
            return self.target_factory.classification_up_down(df, periods=periods)
        if target_spec.startswith("forward_return"):
            parts = target_spec.split("_")
            periods = int(parts[-1]) if parts[-1].isdigit() else 1
            return self.target_factory.forward_return(df, periods=periods)
        if target_spec.startswith("volatility"):
            parts = target_spec.split("_")
            periods = int(parts[-1]) if parts[-1].isdigit() else 1
            return self.target_factory.volatility(df, periods=periods)
        raise ValueError(f"unsupported target spec: {target_spec}")

    def run(self, experiment: ExpType, timeframe: str = "1d") -> ExperimentResultSimple:

        market = experiment.market
        model_name = experiment.model
        target_spec = experiment.target

        # load dataset
        df = self._load_dataset(market, timeframe)

        # optional sampling to limit CPU/time for local test runs
        # sampling is opt-in via allow_sampling to avoid silent changes to production runs
        if self.allow_sampling:
            try:
                import os
                sample_frac = float(os.environ.get("AQRS_SAMPLE_FRAC", "1.0"))
            except Exception:
                sample_frac = 1.0
            if 0.0 < sample_frac < 1.0:
                df = df.sample(frac=sample_frac, random_state=42).reset_index(drop=True)

        # build features
        df = self.feature_factory.build(df)

        # build target
        df["target"] = self._parse_target(df, target_spec)

        # select numeric features
        features = [
            c
            for c in df.columns
            if str(df[c].dtype) in ["float64", "int64", "bool"]
        ]
        if "target" in features:
            features.remove("target")

        # drop rows missing selected features or target
        df = df.dropna(subset=features + ["target"]) if len(features) > 0 else df

        X = df[features]
        y = df["target"]

        if len(df) == 0 or X.shape[1] == 0 or len(y) == 0:
            return ExperimentResultSimple(
                market=market,
                timeframe=timeframe,
                model=model_name,
                target=target_spec,
                accuracy=None,
                rows=len(df),
            )

        split = int(len(df) * 0.8)
        X_train = X.iloc[:split]
        X_test = X.iloc[split:]
        y_train = y.iloc[:split]
        y_test = y.iloc[split:]

        model_impl = self._get_model_impl(model_name)
        trained = model_impl.train(X_train, y_train)

        pred = trained.predict(X_test)

        # detect classification vs regression by dtype of y
        if str(y.dtype).startswith("int") or set(y.unique()) <= {0, 1}:
            metrics = self.metrics.classification_metrics(y_test, pred)
            return ExperimentResultSimple(
                market=market,
                timeframe=timeframe,
                model=model_name,
                target=target_spec,
                accuracy=metrics.get("accuracy"),
                precision=metrics.get("precision"),
                recall=metrics.get("recall"),
                f1=metrics.get("f1"),
                rows=len(df),
            )
        else:
            metrics = self.metrics.regression_metrics(y_test, pred)
            return ExperimentResultSimple(
                market=market,
                timeframe=timeframe,
                model=model_name,
                target=target_spec,
                accuracy=None,
                rows=len(df),
            )
# end of file
