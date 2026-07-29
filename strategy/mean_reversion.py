"""
Mean Reversion strategy: bets that price extremes relative to a
rolling average tend to revert back toward that average.
"""

import pandas as pd
from strategy.base import Strategy, Signal


class MeanReversion(Strategy):
    """
    Bollinger Band-style mean reversion.
    BUY on the bar where price first drops below (mean - k*std) —
    betting the price will revert back upward.
    SELL on the bar where price first rises above (mean + k*std) —
    betting the price will revert back downward.

    Only triggers on the initial crossing into each band, not every
    bar the condition remains true — without this, a stop-loss exit
    followed by price still sitting below the lower band would cause
    an immediate re-entry, and repeat every bar until price genuinely
    moves back inside the bands. That whipsaw pattern was caught and
    fixed during backtesting (see project write-up).
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

        below_lower = data["close"] < lower_band
        above_upper = data["close"] > upper_band

        # Same crossing-detection pattern as MovingAverageCrossover:
        # only fire on the bar where the condition first becomes true.
        entered_below = below_lower & (~below_lower.shift(1, fill_value=False))
        entered_above = above_upper & (~above_upper.shift(1, fill_value=False))

        signals[entered_below] = Signal.BUY
        signals[entered_above] = Signal.SELL

        return signals