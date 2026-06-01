from app.data.providers.binance.provider import (
    BinanceProvider,
)

from app.data.providers.dukascopy.provider import (
    DukascopyProvider,
)

def create_provider(
    provider_name: str,
):

    if provider_name == "binance":
        return BinanceProvider()

    if provider_name == "dukascopy":
        return DukascopyProvider()

    raise ValueError(
        f"unknown provider: {provider_name}"
    )
