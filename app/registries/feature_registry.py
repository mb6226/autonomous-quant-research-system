FEATURES = [
    "return_1",
    "ema20",
    "ema50",
    "ema200",
    "rsi14",
    "atr14",
]


class FeatureRegistry:

    def all(self):
        return FEATURES

    def exists(
        self,
        feature: str,
    ) -> bool:
        return feature in FEATURES
