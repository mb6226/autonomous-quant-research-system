import numpy as np
import pandas as pd


class FeatureFactory:

    def build(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        # Returns

        df["return_1"] = (
            df["close"].pct_change()
        )

        df["log_return_1"] = np.log(
            df["close"]
            / df["close"].shift(1)
        )

        # EMA

        df["ema20"] = (
            df["close"]
            .ewm(span=20)
            .mean()
        )

        df["ema50"] = (
            df["close"]
            .ewm(span=50)
            .mean()
        )

        df["ema200"] = (
            df["close"]
            .ewm(span=200)
            .mean()
        )

        # RSI 14

        delta = (
            df["close"]
            .diff()
        )

        gain = delta.clip(
            lower=0
        )

        loss = (
            -delta.clip(
                upper=0
            )
        )

        avg_gain = (
            gain.rolling(14)
            .mean()
        )

        avg_loss = (
            loss.rolling(14)
            .mean()
        )

        rs = avg_gain / avg_loss

        df["rsi14"] = (
            100
            - (
                100
                / (1 + rs)
            )
        )

        # ATR 14

        high_low = (
            df["high"]
            - df["low"]
        )

        high_close = abs(
            df["high"]
            - df["close"].shift()
        )

        low_close = abs(
            df["low"]
            - df["close"].shift()
        )

        tr = pd.concat(
            [
                high_low,
                high_close,
                low_close,
            ],
            axis=1,
        ).max(axis=1)

        df["atr14"] = (
            tr.rolling(14)
            .mean()
        )

        return df
