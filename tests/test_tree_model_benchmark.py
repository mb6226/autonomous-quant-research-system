import os
import json
from pprint import pprint

from app.research.experiment_runner import ExperimentRunner
from app.research.experiment_generator import Experiment


def run_benchmark():
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    runner = ExperimentRunner(allow_sampling=False)

    market = "BTCUSDT"
    timeframe = "1d"
    target_spec = "classification_up_down_5"

    models = ["random_forest", "xgboost", "lightgbm", "catboost"]

    results = []

    sample_frac = float(os.environ.get("AQRS_SAMPLE_FRAC", "1.0"))

    for m in models:
        exp = Experiment(market=market, model=m, target=target_spec, feature_set="default")
        print(f"\nRunning: {m}")

        # run and collect result
        res = runner.run(exp, timeframe=timeframe)

        # attempt to re-load dataset to print diagnostics for reproducibility
        df = runner._load_dataset(market, timeframe)
        if 0.0 < sample_frac < 1.0:
            df = df.sample(frac=sample_frac, random_state=42).reset_index(drop=True)
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
        split = int(len(df) * 0.8)
        X_train = df[features].iloc[:split]
        X_test = df[features].iloc[split:]
        y_train = df["target"].iloc[:split]
        y_test = df["target"].iloc[split:]

        print("SAMPLE_FRAC:", sample_frac)
        print("TRAIN", len(X_train))
        print("TEST", len(X_test))
        print("y_train unique:", sorted(list(set(y_train.tolist()))))
        print("y_test unique:", sorted(list(set(y_test.tolist()))))

        results.append({
            "model": m,
            "accuracy": res.accuracy,
            "precision": res.precision,
            "recall": res.recall,
            "f1": res.f1,
            "train_rows": len(X_train),
            "test_rows": len(X_test),
        })

    # Sort by accuracy desc
    sorted_results = sorted(results, key=lambda r: (r["accuracy"] is not None, r["accuracy"] or 0), reverse=True)

    # persist canonical benchmark results (trim to required fields)
    canonical = []
    for r in sorted_results:
        canonical.append({
            "model": r["model"],
            "accuracy": r["accuracy"],
            "precision": r["precision"],
            "recall": r["recall"],
            "f1": r["f1"],
        })

    try:
        out_dir = "artifacts"
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "tree_model_benchmark.json")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(canonical, fh, indent=2)
        print("\nSaved canonical benchmark results to ", out_path)
    except Exception as e:
        print("Failed to save canonical benchmark results:", e)

    print("\nMODEL COMPARISON\n")
    print("model, accuracy, precision, recall, f1")
    for r in canonical:
        print(f"{r['model']}, {r['accuracy']}, {r['precision']}, {r['recall']}, {r['f1']}")


if __name__ == "__main__":
    run_benchmark()
