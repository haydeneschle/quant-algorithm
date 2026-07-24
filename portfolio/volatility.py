import pandas as pd


def compute_atr(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Average True Range — a standard measure of recent volatility.
    Higher ATR = more volatile/wider price swings recently.
    """
    high, low, close = data["high"], data["low"], data["close"]

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return true_range.ewm(alpha=1 / window, adjust=False).mean()


def volatility_scalar(current_atr: float, average_atr: float,
                       min_scalar: float = 0.5, max_scalar: float = 1.5) -> float:
    if average_atr == 0 or current_atr == 0 or pd.isna(current_atr) or pd.isna(average_atr):
        return 1.0  # not enough data yet to judge volatility — use neutral sizing

    ratio = average_atr / current_atr
    return max(min_scalar, min(max_scalar, ratio))