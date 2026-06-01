TARGETS = [
    # Regression
    "forward_return_1",
    "forward_return_5",
    "forward_return_10",
    "forward_return_20",

    # Classification
    "classification_up_down",

    # Volatility
    "volatility_5",
    "volatility_10",
    "volatility_20",
]


class TargetRegistry:

    def all(self):
        return TARGETS

    def exists(
        self,
        target: str,
    ) -> bool:
        return target in TARGETS
