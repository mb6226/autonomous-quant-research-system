from app.research.metrics import (
    MetricsEngine,
)

y_true = [1, 2, 3, 4, 5]

y_pred = [1.1, 1.9, 3.2, 3.8, 4.9]

metrics = (
    MetricsEngine()
    .regression_metrics(
        y_true,
        y_pred,
    )
)

print(metrics)
