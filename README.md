# Algorithmic Trading Research Bot
 
A Python framework for building, backtesting, and comparing systematic trading strategies against real historical market data — built to explore whether simple, well-known technical strategies can actually generate risk-adjusted returns once realistic trading costs are accounted for.
 
This project was built as a self-directed way to combine my Computer Science background with an interest in quantitative finance and risk analytics, ahead of applying to internships.
 
---
 
## What it does
 
- Pulls historical price data for any stock via the [Alpaca](https://alpaca.markets) API, with local caching
- Implements two independent trading strategies (Moving Average Crossover and Mean Reversion) behind a shared, pluggable interface
- Combines both into a regime-switching strategy that picks the more suitable strategy per bar, based on an ADX (Average Directional Index) trend-strength measure
- Runs a full backtest (position sizing, stop-losses, transaction cost) through a custom event-driven engine
- Benchmarks every result against simply buying and holding the same stock, and reports return, Sharpe ratio, max drawdown, and win rate
- Includes a dynamic risk-sizing system modeled on a CPU branch predictor's saturating counter, adjusting position size based on recent trade performance
---
 
## Architecture
 
```
data/         →  historical data loading + local caching
strategy/     →  Strategy interface + concrete strategies (MA crossover, mean reversion, regime switching)
portfolio/    →  position tracking, P&L, risk governor, volatility-based sizing
backtest/     →  event-driven backtest engine + performance metrics
config.py     →  central settings (symbols, dates, strategy parameters)
main.py       →  runs the full comparison across strategies and symbols
```
 
The core design is **event-driven**: every strategy exposes the same `generate_signals()` interface, and the portfolio exposes a single `process_signal()` entry point that both the backtester and (eventually) a live paper-trading loop can call identically — no duplicated logic between simulation and real execution.
 
---
 
## Headline finding
 
Early testing suggested Mean Reversion and the regime-switching strategy meaningfully outperformed a simple moving-average crossover on a risk-adjusted basis. Once a realistic per-trade transaction cost (covering spread and commission) was added, that apparent edge almost entirely disappeared; all three strategies converged to similarly weak, near-zero or negative Sharpe ratios.
 
The higher-frequency strategies had looked better mainly because they were trading often on a backtest that assumed trading was free. This turned out to be the most useful result in the project: a strategy's apparent edge can be an artifact of an unrealistic backtest, and it's worth deliberately stress-testing a promising result before trusting it.
 
Across every period and stock tested, simply buying and holding also outperformed every active strategy built here; consistent with the well-documented difficulty simple technical strategies have keeping up during a sustained bull market.
 
---
 
## Improvements to be made
 
- Validate strategy parameters with a proper train/test split, to guard against overfitting to the specific historical periods tested
- Test across multiple individual years (including a down year) rather than one period at a time
- Wire the system to Alpaca's paper trading API for live, simulated execution
- Explore portfolio-level diversification across multiple symbols at once, rather than testing each in isolation
---
 
## A note on scope
 
This project is a research and engineering exercise, not a claim to have found a profitable trading strategy; real, sustained trading edges are hard to find and rarer still to prove with a backtest. The value here is in the testing methodology: isolating variables, benchmarking against a fair baseline, and being willing to let a result overturn an initial hypothesis.