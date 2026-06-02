import os
from pprint import pprint

from app.research.walk_forward_validator import WalkForwardValidator
from app.research.experiment_runner import ExperimentRunner
from app.research.experiment_generator import Experiment


def test_walk_forward_validation():
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    runner = ExperimentRunner(allow_sampling=False)

    market = "BTCUSDT"
    timeframe = "1d"
    target_spec = "classification_up_down_5"

    df = runner._load_dataset(market, timeframe)
    df = runner.feature_factory.build(df)
    df["target"] = runner._parse_target(df, target_spec)

    features = [
        c
        for c in df.columns
        if str(df[c].dtype) in ["float64", "int64", "bool"]
    ]
    if "target" in features:
        features.remove("target")

    df = df.dropna(subset=features + ["target"]) if len(features) > 0 else df

    X = df[features]
    y = df["target"]

    validator = WalkForwardValidator()

    # model factory that returns a fresh model impl
    model_factory = lambda: runner._get_model_impl("xgboost")

    result = validator.run(model_factory, X, y)

    print("Fold Results:")
    for i, f in enumerate(result.folds, start=1):
        print(f"Fold {i}: train_end={f.train_end}, test_end={f.test_end}, accuracy={f.accuracy}")

    print("Average Metrics:")
    pprint({
        "avg_accuracy": result.avg_accuracy,
        "avg_precision": result.avg_precision,
        "avg_recall": result.avg_recall,
        "avg_f1": result.avg_f1,
    })

    assert len(result.folds) > 1
    assert result.avg_accuracy is not None and result.avg_accuracy > 0


if __name__ == "__main__":
    test_walk_forward_validation()
