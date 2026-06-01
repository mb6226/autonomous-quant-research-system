from abc import ABC, abstractmethod

class BaseDataProvider(ABC):

    @abstractmethod
    def load_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ):
        pass
