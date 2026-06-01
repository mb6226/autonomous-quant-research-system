import pandas as pd


class TargetFactory:

    def forward_return(
        self,
        df: pd.DataFrame,
        periods: int,
    ) -> pd.Series:

        return (
            df["close"].shift(-periods)
            / df["close"]
            - 1
        )

    def classification_up_down(
        self,
        df: pd.DataFrame,
        periods: int = 1,
    ) -> pd.Series:

        future_return = (
            df["close"].shift(-periods)
            / df["close"]
            - 1
        )

        return (
            future_return > 0
        ).astype(int)

    def volatility(
        self,
        df: pd.DataFrame,
        periods: int,
    ) -> pd.Series:

        returns = (
            df["close"]
            .pct_change()
        )

        return (
            returns
            .rolling(periods)
            .std()
        )
