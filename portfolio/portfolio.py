from typing import Dict, Optional
from portfolio.position import Position
from portfolio.risk import RiskGovernor, RiskState
from strategy.base import Signal


class Portfolio:
    def __init__(self, initial_capital: float,
                 risk_governor: Optional[RiskGovernor] = None):
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.risk_governor = risk_governor or RiskGovernor(starting_state=RiskState.WEAKLY_CONSERVATIVE)
        self.closed_trades = []
        self.equity_curve = []

    def total_equity(self, current_prices: Dict[str, float]) -> float:
        equity = self.cash
        for symbol, pos in self.positions.items():
            equity += pos.market_value(current_prices.get(symbol, pos.entry_price))
        return equity

    def _position_size(self, symbol: str, price: float) -> float:
        """Determine how many shares to buy based on current risk profile."""
        profile = self.risk_governor.current_profile
        allocation = self.total_equity({symbol: price}) * profile.max_position_size
        return allocation // price  # whole shares only

    def process_signal(self, symbol: str, signal: Signal, price: float, timestamp) -> None:
        profile = self.risk_governor.current_profile

        if signal == Signal.BUY and symbol not in self.positions:
            if len(self.positions) >= profile.max_open_positions:
                return  # risk governor caps concurrent positions

            qty = self._position_size(symbol, price)
            cost = qty * price
            if qty > 0 and cost <= self.cash:
                self.cash -= cost
                self.positions[symbol] = Position(symbol=symbol, quantity=qty, entry_price=price)

        elif signal == Signal.SELL and symbol in self.positions:
            self._close_position(symbol, price)

        self._check_stop_losses(current_prices={symbol: price})
        self.equity_curve.append((timestamp, self.total_equity({symbol: price})))

    def _close_position(self, symbol: str, price: float) -> None:
        pos = self.positions.pop(symbol)
        proceeds = pos.quantity * price
        pnl = pos.unrealized_pnl(price)
        self.cash += proceeds
        self.closed_trades.append(pnl)
        self.risk_governor.record_trade_result(pnl)

    def _check_stop_losses(self, current_prices: Dict[str, float]) -> None:
        profile = self.risk_governor.current_profile
        for symbol in list(self.positions.keys()):
            pos = self.positions[symbol]
            price = current_prices.get(symbol, pos.entry_price)
            loss_pct = (pos.entry_price - price) / pos.entry_price
            if loss_pct >= profile.stop_loss_pct:
                self._close_position(symbol, price)