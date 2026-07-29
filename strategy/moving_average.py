"""
Moving Average Crossover strategy: a classic trend-following approach
that reacts to a shorter-term average crossing a longer-term one.
"""

import pandas as pd
from strategy.base import Strategy, Signal


class MovingAverageCrossover(Strategy):
    """
    Golden cross / death cross strategy.
    BUY when the short-window moving average crosses above the
    long-window moving average (suggests building upward momentum).
    SELL when it crosses back below (suggests momentum turning down).

    This is a lagging strategy by nature — a crossover can only be
    detected after the price has already started moving, so signals
    are always a step behind the actual turning point.
    """

    def __init__(self, short_window: int = 20, long_window: int = 50):
        super().__init__(name="Moving Average Crossover")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        short_ma = data["close"].rolling(window=self.short_window).mean()
        long_ma = data["close"].rolling(window=self.long_window).mean()

        signals = pd.Series(Signal.HOLD, index=data.index)

        # Detect the crossing point itself, not just "short MA is above
        # long MA" — otherwise every bar in an existing uptrend would
        # re-fire BUY, rather than only the bar where it first crosses.
        above = short_ma > long_ma
        crossed_up = above & (~above.shift(1, fill_value=False))
        crossed_down = (~above) & (above.shift(1, fill_value=False))

        signals[crossed_up] = Signal.BUY
        signals[crossed_down] = Signal.SELL

        return signals