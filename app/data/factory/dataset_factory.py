from app.research.market_registry import (
    MARKETS,
)

class DatasetFactory:

    def create(
        self,
        symbol: str,
        timeframe: str,
    ):

        if symbol not in MARKETS:
            raise ValueError(
                f"unsupported symbol: {symbol}"
            )

        return {
            "symbol": symbol,
            "timeframe": timeframe,
        }
