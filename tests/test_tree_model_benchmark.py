import os
from pprint import pprint

from app.research.experiment_runner import ExperimentRunner
from app.research.experiment_generator import Experiment


def run_benchmark():
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    runner = ExperimentRunner()

    market = "BTCUSDT"
    timeframe = "1d"
    target_spec = "classification_up_down_5"

    models = ["random_forest", "xgboost", "lightgbm", "catboost"]

    results = []
    for m in models:
        exp = Experiment(market=market, model=m, target=target_spec, feature_set="default")
        print(f"Running: {m}")
        res = runner.run(exp, timeframe=timeframe)
        # res is ExperimentResultSimple
        results.append({
            "model": m,
            "accuracy": res.accuracy,
            "precision": res.precision,
            "recall": res.recall,
            "f1": res.f1,
        })

    # Sort by accuracy desc
    sorted_results = sorted(results, key=lambda r: (r["accuracy"] is not None, r["accuracy"] or 0), reverse=True)

    print("\nMODEL COMPARISON\n")
    print("model, accuracy, precision, recall, f1")
    for r in sorted_results:
        print(f"{r['model']}, {r['accuracy']}, {r['precision']}, {r['recall']}, {r['f1']}")


if __name__ == "__main__":
    run_benchmark()
