import pandas as pd
from strategy.base import Strategy, Signal

class MovingAverageCrossover(Strategy):
    """
    Golden cross / death cross strategy
    BUY when short MA crosses above long MA
    Sell when short MA crosses below long MA
    """

    def __init__(self, short_window: int = 20, long_window: int = 50):
        super().__init__(name = "Moving Average Crossover")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        short_ma = data["close"].rolling(window = self.short_window).mean()
        long_ma = data["close"].rolling(window = self.long_window).mean()

        signals = pd.Series(Signal.HOLD, index = data.index)

        above = short_ma > long_ma
        crossed_up = above & (~above.shift(1, fill_value=False))
        crossed_down = (~above) & (above.shift(1, fill_value=False))

        signals[crossed_up] = Signal.BUY
        signals[crossed_down] = Signal.SELL

        return signals