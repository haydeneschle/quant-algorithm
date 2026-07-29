"""
Abstract base class defining the interface every trading strategy
must implement. Keeping this interface small and consistent is what
lets the backtest engine, portfolio, and regime-switching meta-strategy
all treat every strategy interchangeably.
"""

from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd


class Signal(Enum):
    """The three possible actions a strategy can output for a given bar."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    Every concrete strategy must implement generate_signals(),
    taking historical price data and returning a signal per bar.

    This is the one interface the rest of the system depends on —
    the backtest engine, the portfolio, and the regime-switching
    meta-strategy all call generate_signals() without knowing or
    caring which concrete strategy they're working with.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Given a DataFrame of OHLCV data (indexed by timestamp),
        return a pandas Series of Signal values, same index as `data`.
        """
        raise NotImplementedError

    def __repr__(self):
        return f"<Strategy: {self.name}>"