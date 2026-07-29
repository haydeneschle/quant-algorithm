"""
Regime-switching meta-strategy: uses ADX (a trend-strength indicator)
to decide, on a per-bar basis, whether the market currently looks
trending or range-bound, and defers to whichever underlying strategy
suits that regime.
"""

import pandas as pd
from strategy.base import Strategy, Signal
from strategy.moving_average import MovingAverageCrossover
from strategy.mean_reversion import MeanReversion


def compute_adx(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Average Directional Index (ADX) — Wilder's classic trend-strength indicator.
    Values above ~25 conventionally indicate a trending market;
    values below ~20 conventionally indicate a range-bound/choppy market.

    Requires 'high', 'low', and 'close' columns in `data`.
    """
    high, low, close = data["high"], data["low"], data["close"]

    # Directional movement: how much price moved up vs. down bar-to-bar.
    # Only the larger of the two (up-move vs. down-move) counts for a
    # given bar — this is Wilder's original convention, not a simplification.
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    plus_dm[(plus_dm - minus_dm) < 0] = 0
    minus_dm[(minus_dm - plus_dm) < 0] = 0

    # True range accounts for gaps between bars, not just the current
    # bar's high-low spread.
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Wilder's smoothing is an EMA with alpha = 1/window, not a simple
    # moving average — this matches the standard ADX definition.
    atr = true_range.ewm(alpha=1 / window, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1 / window, adjust=False).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1 / window, adjust=False).mean() / atr)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.ewm(alpha=1 / window, adjust=False).mean()

    return adx


class RegimeSwitchingStrategy(Strategy):
    """
    Meta-strategy that uses ADX to detect the current market regime,
    and switches between MA Crossover (for trending regimes) and
    Mean Reversion (for range-bound regimes) on a per-bar basis.

    This directly encodes an empirical finding from earlier backtesting:
    MA Crossover performed better on trending symbols (e.g. NVDA) and
    Mean Reversion performed better on range-bound ones (e.g. KO, JNJ) —
    rather than picking one strategy upfront for a symbol, the regime
    detector picks per bar, letting the classification adapt as a
    symbol's behaviour changes over time.

    Note: this reacts to the *current* regime rather than predicting an
    upcoming shift, so there's inherent lag right at regime transitions —
    the same limitation MA Crossover itself has, one level up.
    """

    def __init__(self, adx_threshold: float = 25.0,
                 adx_window: int = 14,
                 trend_strategy: Strategy = None,
                 range_strategy: Strategy = None):
        super().__init__(name="Regime Switching")
        self.adx_threshold = adx_threshold
        self.adx_window = adx_window
        # Allow injecting different strategy instances/params for testing,
        # but default to the standard versions used elsewhere in the project.
        self.trend_strategy = trend_strategy or MovingAverageCrossover()
        self.range_strategy = range_strategy or MeanReversion()

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        adx = compute_adx(data, window=self.adx_window)

        # Both sub-strategies compute their full signal series up front;
        # we then pick per-bar which one to trust based on the regime.
        trend_signals = self.trend_strategy.generate_signals(data)
        range_signals = self.range_strategy.generate_signals(data)

        is_trending = adx > self.adx_threshold

        signals = pd.Series(Signal.HOLD, index=data.index)
        signals[is_trending] = trend_signals[is_trending]
        signals[~is_trending] = range_signals[~is_trending]

        return signals