MODELS = [
    # Linear
    "linear_regression",
    "ridge",
    "lasso",
    "elastic_net",

    # Tree
    "random_forest",
    "extra_trees",

    # Boosting
    "gradient_boosting",
    "xgboost",
    "lightgbm",
    "catboost",

    # SVM
    "svr",
    "svc",

    # Neural Networks
    "mlp",
    "lstm",
    "gru",
    "transformer",
]


class ModelRegistry:

    def all(self):
        return MODELS

    def exists(
        self,
        model: str,
    ) -> bool:
        return model in MODELS
