import os
import json
from app.research.stability_validator import StabilityValidator
from app.research.experiment_runner import ExperimentRunner


def test_mlp_stability(tmp_path, monkeypatch):
    # prepare dataset in temp cwd
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

    sv = StabilityValidator(seeds=[42, 123, 456, 789, 999])
    out_path = os.path.join(str(tmp_path), "artifacts", "mlp_stability.json")
    summary = sv.run_mlp_stability(X, y, out_path=out_path)

    assert os.path.exists(out_path)
    with open(out_path, "r") as f:
        data = json.load(f)

    assert "mean_accuracy" in data
    assert "std_accuracy" in data
    assert isinstance(data["mean_accuracy"], float)
    assert isinstance(data["std_accuracy"], float)
