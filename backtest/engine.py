import pandas as pd
from typing import List
from strategy.base import Strategy
from portfolio.portfolio import Portfolio


class BacktestEngine:
    """
    Event-driven backtest loop: for each historical bar, gets the
    strategy's signal and feeds it to the portfolio for execution.
    """

    def __init__(self, data: pd.DataFrame, strategy: Strategy, portfolio: Portfolio):
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self) -> Portfolio:
        signals = self.strategy.generate_signals(self.data)

        for timestamp, row in self.data.iterrows():
            signal = signals.loc[timestamp]
            price = row["close"]
            symbol = self.data.attrs.get("symbol", "UNKNOWN")

            self.portfolio.process_signal(
                symbol=symbol,
                signal=signal,
                price=price,
                timestamp=timestamp,
            )

        return self.portfolio