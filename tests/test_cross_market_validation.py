import os
from app.research.cross_market_validator import CrossMarketValidator


def test_cross_market_validation_basic():
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    models = ["lightgbm", "mlp", "catboost", "xgboost", "random_forest", "extra_trees"]
    markets = ["BTCUSDT", "EURUSD", "XAUUSD", "USOIL", "US30"]

    v = CrossMarketValidator(allow_sampling=True, sample_frac=0.2)
    res = v.run(models, markets, "1d", "classification_up_down_5")

    assert "results_path" in res and "ranking_path" in res

    # load artifacts
    import json

    with open(res["results_path"], "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(res["ranking_path"], "r", encoding="utf-8") as f:
        ranking = json.load(f)

    assert data, "cross market results should not be empty"
    assert ranking, "ranking should not be empty"

    # ensure all markets present for each model (keys may exist with nulls)
    for m in models:
        assert m in data
        for mk in markets:
            assert mk in data[m]["per_market_results"]
