from dataclasses import dataclass
from typing import Any, Callable, List
from app.research.metrics import MetricsEngine


@dataclass
class FoldResult:
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    accuracy: float | None
    precision: float | None
    recall: float | None
    f1: float | None


@dataclass
class WalkForwardResult:
    folds: List[FoldResult]
    avg_accuracy: float | None
    avg_precision: float | None
    avg_recall: float | None
    avg_f1: float | None


class WalkForwardValidator:
    """Simple walk-forward validator using expanding training windows.

    Parameters:
    - train_stops: list of fractions indicating train end points (e.g. [0.6,0.7,0.8,0.9])
    - test_width: fraction width of each test window (default 0.1)
    """

    def __init__(self, train_stops: List[float] = None, test_width: float = 0.1):
        self.train_stops = train_stops or [0.6, 0.7, 0.8, 0.9]
        self.test_width = test_width
        self.metrics = MetricsEngine()

    def run(self, model_factory: Callable[[], Any], X, y) -> WalkForwardResult:
        n = len(X)
        folds: List[FoldResult] = []

        for train_frac in self.train_stops:
            train_end = int(n * train_frac)
            test_end = int(n * (train_frac + self.test_width))
            if test_end <= train_end:
                continue

            X_train = X.iloc[:train_end]
            X_test = X.iloc[train_end:test_end]
            y_train = y.iloc[:train_end]
            y_test = y.iloc[train_end:test_end]

            if len(X_test) == 0 or len(X_train) == 0:
                continue

            model_impl = model_factory()
            trained = model_impl.train(X_train, y_train)
            pred = trained.predict(X_test)

            metrics = self.metrics.classification_metrics(y_test, pred)

            fr = FoldResult(
                train_start=0,
                train_end=train_end,
                test_start=train_end,
                test_end=test_end,
                accuracy=metrics.get("accuracy"),
                precision=metrics.get("precision"),
                recall=metrics.get("recall"),
                f1=metrics.get("f1"),
            )
            folds.append(fr)

        if not folds:
            return WalkForwardResult(folds=[], avg_accuracy=None, avg_precision=None, avg_recall=None, avg_f1=None)

        # compute averages (skip None)
        def avg(field: str):
            vals = [getattr(f, field) for f in folds if getattr(f, field) is not None]
            return sum(vals) / len(vals) if vals else None

        return WalkForwardResult(
            folds=folds,
            avg_accuracy=avg("accuracy"),
            avg_precision=avg("precision"),
            avg_recall=avg("recall"),
            avg_f1=avg("f1"),
        )
