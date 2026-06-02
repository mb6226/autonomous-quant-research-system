try:
    from catboost import CatBoostClassifier as _CatBoostClassifier
    _HAS_CATBOOST = True
except Exception:
    _HAS_CATBOOST = False

from sklearn.ensemble import GradientBoostingClassifier


class CatBoostClassifierModel:

    def __init__(self, iterations=300, depth=6, learning_rate=0.05, verbose=False, random_state: int = 42):
        self.iterations = iterations
        self.depth = depth
        self.learning_rate = learning_rate
        self.verbose = verbose
        self.random_state = random_state

    def train(self, X, y):
        # Prefer CatBoost if available, otherwise fallback to sklearn's GradientBoosting
        if _HAS_CATBOOST:
            model = _CatBoostClassifier(
                iterations=self.iterations,
                depth=self.depth,
                learning_rate=self.learning_rate,
                verbose=self.verbose,
                random_state=self.random_state,
            )
        else:
            model = GradientBoostingClassifier(
                n_estimators=self.iterations,
                max_depth=self.depth,
                learning_rate=self.learning_rate,
                random_state=self.random_state,
            )

        model.fit(X, y)
        return model
