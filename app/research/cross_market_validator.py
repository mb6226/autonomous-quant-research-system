import json
import os
from typing import List, Dict, Any

from app.research.walk_forward_validator import WalkForwardValidator
from app.research.experiment_runner import ExperimentRunner


class CrossMarketValidator:
    def __init__(self, allow_sampling: bool = True, sample_frac: float = 0.2):
        self.runner = ExperimentRunner(allow_sampling=allow_sampling)
        self.validator = WalkForwardValidator()
        self.sample_frac = float(sample_frac)

    def _load_and_prepare(self, market: str, timeframe: str, target: str):
        df = self.runner._load_dataset(market, timeframe)
        # optional lightweight sampling to keep runs quick while preserving order
        if self.runner.allow_sampling and 0.0 < self.sample_frac < 1.0:
            keep = max(1, int(1.0 / self.sample_frac))
            df = df.iloc[::keep].reset_index(drop=True)

        df = self.runner.feature_factory.build(df)
        df["target"] = self.runner._parse_target(df, target)

        features = [c for c in df.columns if str(df[c].dtype) in ["float64", "int64", "bool"]]
        if "target" in features:
            features.remove("target")

        df = df.dropna(subset=features + ["target"]) if len(features) > 0 else df

        X = df[features]
        y = df["target"]
        return X, y

    def run(self, models: List[str], markets: List[str], timeframe: str, target: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        for model_name in models:
            per_market: Dict[str, Any] = {}
            accuracies = []
            precisions = []
            recalls = []
            f1s = []

            for m in markets:
                try:
                    X, y = self._load_and_prepare(m, timeframe, target)
                except Exception as e:
                    per_market[m] = {"error": str(e)}
                    continue

                if X is None or len(X) == 0:
                    per_market[m] = {"avg_accuracy": None, "avg_precision": None, "avg_recall": None, "avg_f1": None}
                    continue

                model_factory = lambda mn=model_name: self.runner._get_model_impl(mn)

                wfv = self.validator.run(model_factory, X, y)

                pm = {
                    "avg_accuracy": wfv.avg_accuracy,
                    "avg_precision": wfv.avg_precision,
                    "avg_recall": wfv.avg_recall,
                    "avg_f1": wfv.avg_f1,
                    "folds": len(wfv.folds),
                }
                per_market[m] = pm

                if wfv.avg_accuracy is not None:
                    accuracies.append(wfv.avg_accuracy)
                if wfv.avg_precision is not None:
                    precisions.append(wfv.avg_precision)
                if wfv.avg_recall is not None:
                    recalls.append(wfv.avg_recall)
                if wfv.avg_f1 is not None:
                    f1s.append(wfv.avg_f1)

            def mean_or_none(xs):
                return sum(xs) / len(xs) if xs else None

            overall = {
                "per_market_results": per_market,
                "overall_average_accuracy": mean_or_none(accuracies),
                "overall_average_precision": mean_or_none(precisions),
                "overall_average_recall": mean_or_none(recalls),
                "overall_average_f1": mean_or_none(f1s),
            }

            results[model_name] = overall

        # persist artifacts
        out_dir = os.path.join(os.getcwd(), "artifacts")
        os.makedirs(out_dir, exist_ok=True)
        cross_path = os.path.join(out_dir, "cross_market_validation.json")
        with open(cross_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # ranking
        ranking = sorted(
            [
                {"model": m, "overall_average_accuracy": (results[m]["overall_average_accuracy"] or 0.0)}
                for m in results
            ],
            key=lambda x: x["overall_average_accuracy"],
            reverse=True,
        )
        ranking_path = os.path.join(out_dir, "cross_market_ranking.json")
        with open(ranking_path, "w", encoding="utf-8") as f:
            json.dump(ranking, f, indent=2)

        return {"results_path": cross_path, "ranking_path": ranking_path, "ranking": ranking}


def quick_run_default():
    models = ["lightgbm", "mlp", "catboost", "xgboost", "random_forest", "extra_trees"]
    markets = ["BTCUSDT", "EURUSD", "XAUUSD", "USOIL", "US30"]
    v = CrossMarketValidator(allow_sampling=True, sample_frac=0.2)
    return v.run(models, markets, "1d", "classification_up_down_5")
