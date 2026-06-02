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

        # Return Features

        df["return_5"] = (
            df["close"]
            .pct_change(5)
        )

        df["return_10"] = (
            df["close"]
            .pct_change(10)
        )

        df["return_20"] = (
            df["close"]
            .pct_change(20)
        )

        df["log_return_5"] = np.log(
            df["close"]
            / df["close"].shift(5)
        )

        df["log_return_20"] = np.log(
            df["close"]
            / df["close"].shift(20)
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

        # Momentum Features

        df["roc_5"] = (
            df["close"]
            / df["close"].shift(5)
            - 1
        )

        df["roc_10"] = (
            df["close"]
            / df["close"].shift(10)
            - 1
        )

        df["roc_20"] = (
            df["close"]
            / df["close"].shift(20)
            - 1
        )

        df["ema20_distance"] = (
            df["close"]
            / df["ema20"]
            - 1
        )

        df["ema50_distance"] = (
            df["close"]
            / df["ema50"]
            - 1
        )

        df["ema200_distance"] = (
            df["close"]
            / df["ema200"]
            - 1
        )

        df["rsi_momentum"] = (
            df["rsi14"]
            - df["rsi14"].shift(5)
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

        # Volatility Features

        df["volatility_5"] = (
            df["return_1"]
            .rolling(5)
            .std()
        )

        df["volatility_10"] = (
            df["return_1"]
            .rolling(10)
            .std()
        )

        df["volatility_20"] = (
            df["return_1"]
            .rolling(20)
            .std()
        )

        df["atr_ratio"] = (
            df["atr14"]
            / df["close"]
        )

        df["high_low_ratio"] = (
            (df["high"] - df["low"]) 
            / df["close"]
        )

        # Trend Features

        df["ema20_diff"] = df["close"] - df["ema20"]
        df["ema50_diff"] = df["close"] - df["ema50"]

        # MACD (12,26) and signal (9)
        ema12 = df["close"].ewm(span=12).mean()
        ema26 = df["close"].ewm(span=26).mean()
        df["macd"] = ema12 - ema26
        df["macd_signal"] = df["macd"].ewm(span=9).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        # 20-period slope (linear fit) computed via diff of ema20
        df["trend_slope_20"] = df["ema20"].diff(20) / 20

        # VWAP

        if "volume" in df.columns:

            pv = (
                df["close"]
                * df["volume"]
            )

            df["vwap"] = (
                pv.cumsum()
                / df["volume"].cumsum()
            )

        return df
