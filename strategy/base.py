from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd

class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    Every strategy must implement generate_signals(),
    taking historical price data and returning a signal per bar.
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