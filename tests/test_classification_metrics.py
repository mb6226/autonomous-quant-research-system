from app.research.metrics import (
    MetricsEngine,
)

y_true = [
    1,1,1,1,1,
    0,0,0,0,0
]

y_pred = [
    1,1,1,0,1,
    0,0,1,0,0
]

metrics = (
    MetricsEngine()
    .classification_metrics(
        y_true,
        y_pred,
    )
)

print(metrics)
