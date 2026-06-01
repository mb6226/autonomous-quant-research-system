MARKETS = [
    "BTCUSDT",
    "EURUSD",
    "XAUUSD",
    "USOIL",
    "US30",
]


class MarketRegistry:

    def all(self):
        return MARKETS

    def exists(
        self,
        market: str,
    ) -> bool:
        return market in MARKETS
