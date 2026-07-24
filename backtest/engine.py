import pandas as pd
from strategy.base import Strategy
from portfolio.portfolio import Portfolio
from portfolio.volatility import compute_atr


class BacktestEngine:
    def __init__(self, data: pd.DataFrame, strategy: Strategy, portfolio: Portfolio):
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self) -> Portfolio:
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