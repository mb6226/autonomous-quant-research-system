from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)


class MetricsEngine:

    def regression_metrics(
        self,
        y_true,
        y_pred,
    ):

        return {
            "mae": mean_absolute_error(
                y_true,
                y_pred,
            ),
            "mse": mean_squared_error(
                y_true,
                y_pred,
            ),
            "r2": r2_score(
                y_true,
                y_pred,
            ),
        }

    def classification_metrics(
        self,
        y_true,
        y_pred,
    ):

        return {
            "accuracy": accuracy_score(
                y_true,
                y_pred,
            ),
            "precision": precision_score(
                y_true,
                y_pred,
                zero_division=0,
            ),
            "recall": recall_score(
                y_true,
                y_pred,
                zero_division=0,
            ),
            "f1": f1_score(
                y_true,
                y_pred,
                zero_division=0,
            ),
        }
