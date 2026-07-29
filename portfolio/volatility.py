"""
Volatility-based position sizing: adjusts how large a position should
be based on a symbol's current volatility relative to its recent
average, independent of the performance-based RiskGovernor.
"""

import pandas as pd


def compute_atr(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Average True Range — a standard measure of recent volatility.
    Higher ATR = more volatile/wider price swings recently.

    Requires 'high', 'low', and 'close' columns in `data`.
    """
    high, low, close = data["high"], data["low"], data["close"]

    # True range accounts for gaps between bars (e.g. overnight moves),
    # not just the current bar's own high-low spread.
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return true_range.ewm(alpha=1 / window, adjust=False).mean()


def volatility_scalar(current_atr: float, average_atr: float,
                       min_scalar: float = 0.5, max_scalar: float = 1.5) -> float:
    """
    Returns a multiplier to apply to position size based on current
    volatility relative to its recent average. Below-average volatility
    scales position size up (toward max_scalar); above-average volatility
    scales it down (toward min_scalar). Clamped at both ends to avoid
    extreme position sizes from a single unusually calm or violent bar.
    """
    # Early bars (before the ATR average has enough data) can produce
    # a zero or NaN value — default to a neutral 1.0x scalar rather
    # than dividing by zero or propagating NaN into position sizing.
    if average_atr == 0 or current_atr == 0 or pd.isna(current_atr) or pd.isna(average_atr):
        return 1.0

    ratio = average_atr / current_atr  # inverse: high current vol -> smaller scalar
    return max(min_scalar, min(max_scalar, ratio))