import os

from app.research.experiment_runner import ExperimentRunner
from app.research.experiment_generator import Experiment


def test_sampling_guard():
    # set a sampling env var
    os.environ["AQRS_SAMPLE_FRAC"] = "0.02"

    exp = Experiment(market="BTCUSDT", model="xgboost", target="classification_up_down_5", feature_set="default")

    # when sampling disabled, row count should be full
    runner_no = ExperimentRunner(allow_sampling=False)
    res_no = runner_no.run(exp, timeframe="1d")

    # when sampling enabled, row count should be reduced
    runner_yes = ExperimentRunner(allow_sampling=True)
    res_yes = runner_yes.run(exp, timeframe="1d")

    assert res_no.rows is not None and res_yes.rows is not None
    assert res_yes.rows < res_no.rows


if __name__ == '__main__':
    test_sampling_guard()
