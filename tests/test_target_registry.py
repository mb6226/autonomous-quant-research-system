from app.registries.target_registry import (
    TargetRegistry,
)

registry = TargetRegistry()

print(
    "COUNT =",
    len(
        registry.all()
    )
)

for target in registry.all():
    print(target)

print(
    "FWD5 =",
    registry.exists(
        "forward_return_5"
    )
)

print(
    "VOL10 =",
    registry.exists(
        "volatility_10"
    )
)

print(
    "FAKE =",
    registry.exists(
        "fake_target"
    )
)
