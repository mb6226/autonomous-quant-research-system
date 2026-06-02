from typing import List, Any


class AutoLeaderboard:
    def __init__(self):
        self._results: List[Any] = []

    def add(self, result: Any) -> None:
        self._results.append(result)

    def add_many(self, results: List[Any]) -> None:
        for r in results:
            self.add(r)

    def _is_classification(self, r: Any) -> bool:
        return hasattr(r, "accuracy") and r.accuracy is not None

    def _is_regression(self, r: Any) -> bool:
        return hasattr(r, "r2") and r.r2 is not None

    def _classification_sorted(self) -> List[Any]:
        return sorted(
            [r for r in self._results if self._is_classification(r)],
            key=lambda x: float(x.accuracy),
            reverse=True,
        )

    def _regression_sorted(self) -> List[Any]:
        return sorted(
            [r for r in self._results if self._is_regression(r)],
            key=lambda x: float(x.r2),
            reverse=True,
        )

    def top(self, n: int = 10) -> List[Any]:
        # Combine classification then regression
        cls = self._classification_sorted()
        reg = self._regression_sorted()
        combined = cls + reg
        return combined[:n]

    def all(self) -> List[Any]:
        # Return combined sorted list
        return self.top(n=len(self._results))
