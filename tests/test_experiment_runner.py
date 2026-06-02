from app.research.experiment_generator import Experiment
from app.research.experiment_runner import ExperimentRunner


def test_run_one_experiment():
    exp = Experiment(market="BTCUSDT", model="xgboost", target="classification_up_down_5", feature_set="default")

    runner = ExperimentRunner()

    result = runner.run(exp, timeframe="1d")

    print(result)

    assert result.market == "BTCUSDT"
    assert result.model == "xgboost"

