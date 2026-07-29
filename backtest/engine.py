"""
Event-driven backtest engine: replays historical data bar-by-bar,
feeding each strategy signal and ATR reading into the portfolio for
execution. Deliberately mirrors how a live trading loop would call
Portfolio, so backtesting and (eventual) live trading share the same
execution path.
"""

import pandas as pd
from strategy.base import Strategy
from portfolio.portfolio import Portfolio
from portfolio.volatility import compute_atr


class BacktestEngine:
    """Runs a single strategy against a single symbol's historical data."""

    def __init__(self, data: pd.DataFrame, strategy: Strategy, portfolio: Portfolio):
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self) -> Portfolio:
        """
        Generate signals for the entire dataset up front (strategies
        are vectorized over the whole series), then step through bar
        by bar feeding each signal and the current/average ATR into
        the portfolio — the portfolio itself decides what to actually
        do with each signal.
        """
        signals = self.strategy.generate_signals(self.data)
        atr = compute_atr(self.data)
        average_atr = atr.mean()
        symbol = self.data.attrs.get("symbol", "UNKNOWN")

        for timestamp, row in self.data.iterrows():
            signal = signals.loc[timestamp]
            price = row["close"]
            current_atr = atr.loc[timestamp]

            self.portfolio.process_signal(
                symbol=symbol,
                signal=signal,
                price=price,
                timestamp=timestamp,
                current_atr=current_atr,
                average_atr=average_atr,
            )

        return self.portfolio