from app.registries.model_registry import (
    ModelRegistry,
)

registry = ModelRegistry()

print("COUNT =", len(registry.all()))

for model in registry.all():
    print(model)

print(
    "XGBOOST =",
    registry.exists("xgboost"),
)

print(
    "LSTM =",
    registry.exists("lstm"),
)

print(
    "FAKE =",
    registry.exists("fake_model"),
)
