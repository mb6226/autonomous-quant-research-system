from app.research.experiment_result import (
    ExperimentResult,
)

result = ExperimentResult(
    experiment_name="btc_rf_v1",
    rows=2344,
    sharpe=1.25,
    sortino=1.80,
    max_drawdown=-0.15,
)

print(result)
