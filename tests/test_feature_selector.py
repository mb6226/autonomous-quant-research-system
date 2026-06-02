from app.research.experiment_generator import Experiment
from app.research.feature_selector import FeatureSelector


def test_feature_selector_basic():
    exp = Experiment(market="BTCUSDT", model="xgboost", target="classification_up_down_5", feature_set="default")

    fs = FeatureSelector()

    ranking = fs.rank_features(exp, timeframe="1d")

    assert len(ranking) > 0

    # ensure sorted descending by delta
    deltas = [d for _, d in ranking]
    assert all(deltas[i] >= deltas[i + 1] for i in range(len(deltas) - 1))

    top = fs.top_features(exp, n=10)

    print("TOP FEATURES")
    for i, (name, delta) in enumerate(top, start=1):
        print(f"{i} {name} {delta:.3f}")
