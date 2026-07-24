from dataclasses import dataclass

@dataclass
class Position:
    """Represents a single open holding in a symbol."""
    symbol: str
    quantity: float
    entry_price: float

    def market_value(self, current_price: float) -> float:
        return self.quantity * current_price

    def unrealized_pnl(self, current_price: float) -> float:
        return (current_price - self.entry_price) * self.quantity