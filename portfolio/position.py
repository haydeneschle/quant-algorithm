"""
Represents a single open holding in a symbol — the basic unit tracked
by Portfolio.
"""

from dataclasses import dataclass


@dataclass
class Position:
    """Represents a single open holding in a symbol."""
    symbol: str
    quantity: float
    entry_price: float

    def market_value(self, current_price: float) -> float:
        """Current worth of this position at the given market price."""
        return self.quantity * current_price

    def unrealized_pnl(self, current_price: float) -> float:
        """
        Profit or loss if this position were closed at the given price,
        without actually closing it — used by Portfolio to check stop-loss
        thresholds each bar before deciding whether to exit.
        """
        return (current_price - self.entry_price) * self.quantity