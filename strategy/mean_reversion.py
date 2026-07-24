# strategy/mean_reversion.py
import pandas as pd
from strategy.base import Strategy, Signal


class MeanReversion(Strategy):
    """
    Bollinger Band-style mean reversion.
    BUY when price drops below (mean - k*std) — assumes it will revert upward.
    SELL when price rises above (mean + k*std) — assumes it will revert downward.
    """

    def __init__(self, window: int = 20, num_std: float = 2.0):
        super().__init__(name="Mean Reversion")
        self.window = window
        self.num_std = num_std

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        rolling_mean = data["close"].rolling(window=self.window).mean()
        rolling_std = data["close"].rolling(window=self.window).std()

        upper_band = rolling_mean + (self.num_std * rolling_std)
        lower_band = rolling_mean - (self.num_std * rolling_std)

        signals = pd.Series(Signal.HOLD, index=data.index)
        signals[data["close"] < lower_band] = Signal.BUY
        signals[data["close"] > upper_band] = Signal.SELL

        return signals