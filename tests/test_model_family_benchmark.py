import os
import json
from pprint import pprint

from app.research.experiment_runner import ExperimentRunner
from app.research.walk_forward_validator import WalkForwardValidator


def run_benchmark_wfv():
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    runner = ExperimentRunner(allow_sampling=False)

    market = "BTCUSDT"
    timeframe = "1d"
    target_spec = "classification_up_down_5"

    models = ["random_forest", "extra_trees", "xgboost", "lightgbm", "catboost", "mlp"]

    results = []

    validator = WalkForwardValidator()

    for m in models:
        print(f"\nRunning WFV benchmark: {m}")

        # load dataset and prepare X,y
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

        model_factory = lambda: runner._get_model_impl(m)
        wfv_result = validator.run(model_factory, X, y)

        print("Folds:", len(wfv_result.folds))
        print("Average accuracy:", wfv_result.avg_accuracy)

        results.append({
            "model": m,
            "folds": len(wfv_result.folds),
            "average_accuracy": wfv_result.avg_accuracy,
            "average_precision": wfv_result.avg_precision,
            "average_recall": wfv_result.avg_recall,
            "average_f1": wfv_result.avg_f1,
        })

    # Sort by average_accuracy desc
    sorted_results = sorted(results, key=lambda r: (r["average_accuracy"] is not None, r["average_accuracy"] or 0), reverse=True)

    # Persist WFV benchmark results for model family
    try:
        out_dir = "artifacts"
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "model_family_benchmark_wfv.json")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(sorted_results, fh, indent=2)
        print("\nSaved WFV benchmark results to ", out_path)
    except Exception as e:
        print("Failed to save WFV benchmark results:", e)

    print("\nMODEL COMPARISON (WFV)\n")
    print("model, folds, average_accuracy, average_precision, average_recall, average_f1")
    for r in sorted_results:
        print(f"{r['model']}, {r['folds']}, {r['average_accuracy']}, {r['average_precision']}, {r['average_recall']}, {r['average_f1']}")


if __name__ == "__main__":
    run_benchmark_wfv()
