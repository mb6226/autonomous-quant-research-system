from app.registries.market_registry import (
    MarketRegistry,
)

registry = MarketRegistry()

print(
    registry.all()
)

print(
    registry.exists(
        "BTCUSDT"
    )
)

print(
    registry.exists(
        "AAPL"
    )
)
