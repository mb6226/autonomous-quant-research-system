from typing import List, Tuple
from app.research.experiment_generator import Experiment
from app.research.experiment_runner import ExperimentRunner
import pandas as pd


class FeatureSelector:

    def __init__(self):
        # disable sampling for feature selection by default
        self.runner = ExperimentRunner(allow_sampling=False)

    def _prepare(self, experiment: Experiment, timeframe: str = "1d") -> tuple[pd.DataFrame, list, pd.Series]:
        df = self.runner._load_dataset(experiment.market, timeframe)
        df = self.runner.feature_factory.build(df)
        df["target"] = self.runner._parse_target(df, experiment.target)

        features = [
            c
            for c in df.columns
            if str(df[c].dtype) in ["float64", "int64", "bool"]
        ]
        if "target" in features:
            features.remove("target")

        df = df.dropna(subset=features + ["target"]) if len(features) > 0 else df

        return df, features, df["target"]

    def rank_features(self, experiment: Experiment, timeframe: str = "1d") -> List[Tuple[str, float]]:
        df, features, y = self._prepare(experiment, timeframe)

        if df.empty or len(features) == 0:
            return []

        X = df[features]

        split = int(len(df) * 0.8)
        X_train = X.iloc[:split]
        X_test = X.iloc[split:]
        y_train = y.iloc[:split]
        y_test = y.iloc[split:]

        model_impl = self.runner._get_model_impl(experiment.model)
        trained = model_impl.train(X_train, y_train)
        pred = trained.predict(X_test)
        baseline = self.runner.metrics.classification_metrics(y_test, pred)["accuracy"]

        deltas = []

        for f in features:
            subset = [c for c in features if c != f]
            if len(subset) == 0:
                new_acc = 0.0
            else:
                Xs = df[subset]
                Xs_train = Xs.iloc[:split]
                Xs_test = Xs.iloc[split:]
                trained2 = model_impl.train(Xs_train, y_train)
                pred2 = trained2.predict(Xs_test)
                new_acc = self.runner.metrics.classification_metrics(y_test, pred2)["accuracy"]

            delta = baseline - new_acc
            deltas.append((f, delta))

        # sort descending by delta
        deltas_sorted = sorted(deltas, key=lambda x: x[1], reverse=True)
        return deltas_sorted

    def top_features(self, experiment: Experiment, n: int = 10, timeframe: str = "1d") -> List[Tuple[str, float]]:
        ranked = self.rank_features(experiment, timeframe)
        return ranked[:n]
