from app.data.providers.base_provider import (
    BaseDataProvider,
)

class BinanceProvider(
    BaseDataProvider
):

    def load_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ):
        raise NotImplementedError
