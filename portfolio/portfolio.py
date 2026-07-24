from typing import Dict, Optional
from portfolio.position import Position
from portfolio.risk import RiskGovernor, RiskState
from portfolio.volatility import volatility_scalar
from strategy.base import Signal

# add near the top of the class or as a config-driven constant
TRANSACTION_COST_PCT = 0.001  # 0.1% per trade (covers spread + commission, a reasonable retail estimate)

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

    def _position_size(self, symbol: str, price: float, vol_scalar: float = 1.0) -> float:
        """Determine how many shares to buy, scaled by current volatility regime."""
        profile = self.risk_governor.current_profile
        base_allocation = self.total_equity({symbol: price}) * profile.max_position_size
        adjusted_allocation = base_allocation * vol_scalar
        return adjusted_allocation // price

    def process_signal(self, symbol: str, signal: Signal, price: float, timestamp,
                        current_atr: float = None, average_atr: float = None) -> None:
        profile = self.risk_governor.current_profile
        vol_scalar = 1.0
        if current_atr is not None and average_atr is not None:
            vol_scalar = volatility_scalar(current_atr, average_atr)

        if signal == Signal.BUY and symbol not in self.positions:
            if len(self.positions) >= profile.max_open_positions:
                return

            qty = self._position_size(symbol, price, vol_scalar)
            cost = qty * price
            transaction_cost = cost * TRANSACTION_COST_PCT
            total_cost = cost + transaction_cost

            if qty > 0 and total_cost <= self.cash:
                self.cash -= total_cost
                self.positions[symbol] = Position(symbol=symbol, quantity=qty, entry_price=price)

        elif signal == Signal.SELL and symbol in self.positions:
            self._close_position(symbol, price)

        self._check_stop_losses(current_prices={symbol: price})
        self.equity_curve.append((timestamp, self.total_equity({symbol: price})))


    def _close_position(self, symbol: str, price: float) -> None:
        pos = self.positions.pop(symbol)
        proceeds = pos.quantity * price
        transaction_cost = proceeds * TRANSACTION_COST_PCT
        net_proceeds = proceeds - transaction_cost

        # P&L now reflects both entry and exit costs
        pnl = net_proceeds - (pos.quantity * pos.entry_price * (1 + TRANSACTION_COST_PCT))

        self.cash += net_proceeds
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