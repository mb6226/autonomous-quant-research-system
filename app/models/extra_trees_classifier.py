from sklearn.ensemble import ExtraTreesClassifier


class ExtraTreesClassifierModel:

    def train(self, X, y):
        model = ExtraTreesClassifier(
            n_estimators=300,
            max_depth=None,
            random_state=42,
            n_jobs=-1,
        )

        model.fit(X, y)
        return model
