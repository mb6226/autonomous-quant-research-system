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
