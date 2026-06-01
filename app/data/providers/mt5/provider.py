from app.data.providers.base_provider import (
    BaseDataProvider,
)

class MT5Provider(
    BaseDataProvider
):

    def load_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ):
        raise NotImplementedError
