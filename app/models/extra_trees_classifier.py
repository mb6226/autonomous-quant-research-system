from sklearn.ensemble import ExtraTreesClassifier


class ExtraTreesClassifierModel:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def train(self, X, y):
        model = ExtraTreesClassifier(
            n_estimators=300,
            max_depth=None,
            random_state=self.random_state,
            n_jobs=-1,
        )

        model.fit(X, y)
        return model
