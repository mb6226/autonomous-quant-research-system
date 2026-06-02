from app.research.experiment_generator import ExperimentGenerator
from app.research.multi_market_runner import MultiMarketRunner
import os


def test_multi_market_runner_prints_summary():
    markets = ["BTCUSDT", "EURUSD", "XAUUSD", "USOIL", "US30"]
    models = ["xgboost"]
    targets = ["classification_up_down_5"]
    feature_sets = ["default"]

    gen = ExperimentGenerator(markets=markets, models=models, targets=targets, feature_sets=feature_sets)
    experiments = gen.generate()

    # limit data to small sample for tests
    os.environ.setdefault("AQRS_SAMPLE_FRAC", "0.05")

    runner = MultiMarketRunner()
    result = runner.run(experiments)

    print("TOTAL EXPERIMENTS", result.total_experiments)
    print("SUCCESSFUL EXPERIMENTS", result.successful_experiments)
    print("FAILED EXPERIMENTS", result.failed_experiments)
    print("TOP 5 LEADERBOARD")
    top = result.leaderboard.top(5)
    for i, r in enumerate(top, start=1):
        print(i, r.market, r.model, r.target, getattr(r, "accuracy", None))

    assert len(result.results) > 0
    assert len(top) > 0
    assert result.successful_experiments >= 0
