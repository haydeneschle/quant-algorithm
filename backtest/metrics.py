import numpy as np
import pandas as pd
from typing import List


def total_return(equity_curve: List[tuple], initial_capital: float) -> float:
    if not equity_curve:
        return 0.0
    final_equity = equity_curve[-1][1]
    return (final_equity - initial_capital) / initial_capital


def sharpe_ratio(equity_curve: List[tuple], risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    if len(equity_curve) < 2:
        return 0.0
    equity_series = pd.Series([e[1] for e in equity_curve])
    returns = equity_series.pct_change().dropna()
    if returns.std() == 0:
        return 0.0
    excess_returns = returns - (risk_free_rate / periods_per_year)
    return np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()


def max_drawdown(equity_curve: List[tuple]) -> float:
    if not equity_curve:
        return 0.0
    equity_series = pd.Series([e[1] for e in equity_curve])
    running_max = equity_series.cummax()
    drawdown = (equity_series - running_max) / running_max
    return drawdown.min()


def win_rate(closed_trades: List[float]) -> float:
    if not closed_trades:
        return 0.0
    wins = sum(1 for pnl in closed_trades if pnl > 0)
    return wins / len(closed_trades)


def summary(portfolio, initial_capital: float) -> dict:
    return {
        "total_return_pct": total_return(portfolio.equity_curve, initial_capital) * 100,
        "sharpe_ratio": sharpe_ratio(portfolio.equity_curve),
        "max_drawdown_pct": max_drawdown(portfolio.equity_curve) * 100,
        "win_rate_pct": win_rate(portfolio.closed_trades) * 100,
        "num_trades": len(portfolio.closed_trades),
    }

def buy_and_hold_return(data) -> float:
    """Return % if you'd simply bought at the first close and held to the last."""
    start_price = data["close"].iloc[0]
    end_price = data["close"].iloc[-1]
    return (end_price - start_price) / start_price * 100