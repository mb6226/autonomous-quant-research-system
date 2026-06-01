from app.registries.feature_registry import (
    FeatureRegistry,
)

registry = FeatureRegistry()

print(
    registry.all()
)

print(
    registry.exists(
        "ema20"
    )
)

print(
    registry.exists(
        "vwap"
    )
)
