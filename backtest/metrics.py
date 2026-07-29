"""
Performance metrics computed from a completed backtest: return
(both total and annualized), Sharpe ratio, max drawdown, and win
rate — plus a buy-and-hold benchmark for comparison.
"""

import numpy as np
import pandas as pd
from typing import List


def total_return(equity_curve: List[tuple], initial_capital: float) -> float:
    """Cumulative return over the entire backtest period, as a fraction (not %)."""
    if not equity_curve:
        return 0.0
    final_equity = equity_curve[-1][1]
    return (final_equity - initial_capital) / initial_capital


def annualized_return(equity_curve: List[tuple], initial_capital: float) -> float:
    """
    Converts cumulative return into a compounded annual rate, so
    results across different time periods (a 1-year backtest vs. a
    5-year one) can be fairly compared. Without this, a 5-year
    cumulative return can look deceptively similar in magnitude to
    a 1-year one despite representing a much lower annual rate.
    """
    if len(equity_curve) < 2:
        return 0.0

    start_date = equity_curve[0][0]
    end_date = equity_curve[-1][0]
    years = (end_date - start_date).days / 365.25

    if years <= 0:
        return 0.0

    cumulative = total_return(equity_curve, initial_capital)
    return (1 + cumulative) ** (1 / years) - 1


def sharpe_ratio(equity_curve: List[tuple], risk_free_rate: float = 0.0,
                  periods_per_year: int = 252) -> float:
    """
    Risk-adjusted return: excess return over the risk-free rate,
    divided by volatility of returns, annualized. periods_per_year=252
    assumes daily bars (trading days/year) — this would need adjusting
    if used on hourly-bar equity curves, since the volatility would
    otherwise be annualized on the wrong basis.
    """
    if len(equity_curve) < 2:
        return 0.0
    equity_series = pd.Series([e[1] for e in equity_curve])
    returns = equity_series.pct_change().dropna()
    if returns.std() == 0:
        return 0.0
    excess_returns = returns - (risk_free_rate / periods_per_year)
    return np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()


def max_drawdown(equity_curve: List[tuple]) -> float:
    """Largest peak-to-trough decline in equity over the backtest, as a negative fraction."""
    if not equity_curve:
        return 0.0
    equity_series = pd.Series([e[1] for e in equity_curve])
    running_max = equity_series.cummax()
    drawdown = (equity_series - running_max) / running_max
    return drawdown.min()


def win_rate(closed_trades: List[float]) -> float:
    """Fraction of closed trades that were profitable."""
    if not closed_trades:
        return 0.0
    wins = sum(1 for pnl in closed_trades if pnl > 0)
    return wins / len(closed_trades)


def buy_and_hold_return(data: pd.DataFrame) -> float:
    """
    Return (%) from simply buying at the first close and holding to
    the last — the baseline every active strategy needs to beat to
    be worth the added complexity and trading costs.
    """
    start_price = data["close"].iloc[0]
    end_price = data["close"].iloc[-1]
    return (end_price - start_price) / start_price * 100


def summary(portfolio, initial_capital: float) -> dict:
    """Bundle every metric into a single dict for easy comparison/printing."""
    return {
        "total_return_pct": total_return(portfolio.equity_curve, initial_capital) * 100,
        "annualized_return_pct": annualized_return(portfolio.equity_curve, initial_capital) * 100,
        "sharpe_ratio": sharpe_ratio(portfolio.equity_curve),
        "max_drawdown_pct": max_drawdown(portfolio.equity_curve) * 100,
        "win_rate_pct": win_rate(portfolio.closed_trades) * 100,
        "num_trades": len(portfolio.closed_trades),
    }