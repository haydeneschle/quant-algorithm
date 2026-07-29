"""
Tracks cash, open positions, and P&L across a backtest (or, eventually,
live trading). This is where the RiskGovernor's performance-based
sizing and the ATR-based volatility scalar both get applied, and where
transaction costs are charged on every trade.
"""

from typing import Dict, Optional
from portfolio.position import Position
from portfolio.risk import RiskGovernor, RiskState
from portfolio.volatility import volatility_scalar
from strategy.base import Signal

# Estimated cost per trade (spread + commission), applied on both
# entry and exit. 0.1% is a reasonable retail estimate, not derived
# from real per-symbol spread data — see project write-up.
TRANSACTION_COST_PCT = 0.001


class Portfolio:
    """
    Owns cash and open positions, and is the single entry point
    (process_signal) that both the backtest engine and, eventually,
    a live trading loop call identically — the same code path handles
    simulated and real execution.
    """

    def __init__(self, initial_capital: float,
                 risk_governor: Optional[RiskGovernor] = None):
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.risk_governor = risk_governor or RiskGovernor(starting_state=RiskState.WEAKLY_CONSERVATIVE)
        self.closed_trades = []  # realized P&L per closed trade, used for win rate etc.
        self.equity_curve = []   # (timestamp, total_equity) snapshots, used for Sharpe/drawdown

    def total_equity(self, current_prices: Dict[str, float]) -> float:
        """Cash plus the current market value of every open position."""
        equity = self.cash
        for symbol, pos in self.positions.items():
            equity += pos.market_value(current_prices.get(symbol, pos.entry_price))
        return equity

    def _position_size(self, symbol: str, price: float, vol_scalar: float = 1.0) -> float:
        """
        Determine how many shares to buy. Base allocation comes from
        the risk governor's current profile (performance-based), then
        vol_scalar (market-based) adjusts it up or down — these are
        two independent risk dimensions that multiply together.
        """
        profile = self.risk_governor.current_profile
        base_allocation = self.total_equity({symbol: price}) * profile.max_position_size
        adjusted_allocation = base_allocation * vol_scalar
        return adjusted_allocation // price  # whole shares only

    def process_signal(self, symbol: str, signal: Signal, price: float, timestamp,
                        current_atr: float = None, average_atr: float = None) -> None:
        """
        Act on a single strategy signal for one bar. current_atr/average_atr
        are optional — when omitted, volatility_scalar defaults to a
        neutral 1.0x, so this still works for strategies/tests that
        don't supply volatility data.
        """
        profile = self.risk_governor.current_profile
        vol_scalar = 1.0
        if current_atr is not None and average_atr is not None:
            vol_scalar = volatility_scalar(current_atr, average_atr)

        if signal == Signal.BUY and symbol not in self.positions:
            # Risk governor caps concurrent open positions
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

        # Stop-losses are checked every bar, not just on a SELL signal —
        # a position can be forced closed even if the strategy hasn't
        # itself issued a SELL yet.
        self._check_stop_losses(current_prices={symbol: price})
        self.equity_curve.append((timestamp, self.total_equity({symbol: price})))

    def _close_position(self, symbol: str, price: float) -> None:
        """
        Close an open position, applying the transaction cost on exit
        (entry cost was already deducted from cash when the position
        was opened), and feed the realized P&L back into the risk
        governor so it can adjust its state for the next trade.
        """
        pos = self.positions.pop(symbol)
        proceeds = pos.quantity * price
        transaction_cost = proceeds * TRANSACTION_COST_PCT
        net_proceeds = proceeds - transaction_cost

        # P&L reflects both entry and exit costs, so it's the true
        # realized profit/loss net of trading frictions.
        pnl = net_proceeds - (pos.quantity * pos.entry_price * (1 + TRANSACTION_COST_PCT))

        self.cash += net_proceeds
        self.closed_trades.append(pnl)
        self.risk_governor.record_trade_result(pnl)

    def _check_stop_losses(self, current_prices: Dict[str, float]) -> None:
        """Force-close any open position that has breached the current
        risk profile's stop-loss threshold."""
        profile = self.risk_governor.current_profile
        for symbol in list(self.positions.keys()):  # list() to allow mutation during iteration
            pos = self.positions[symbol]
            price = current_prices.get(symbol, pos.entry_price)
            loss_pct = (pos.entry_price - price) / pos.entry_price
            if loss_pct >= profile.stop_loss_pct:
                self._close_position(symbol, price)