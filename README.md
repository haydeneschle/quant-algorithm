# Algorithmic Trading Project — Findings So Far
 
## Project Overview
 
A Python-based algorithmic trading system built around an event-driven architecture (data → strategy → portfolio → execution), tested via a custom backtesting engine against Alpaca's historical market data API. The project implements two trading strategies (Moving Average Crossover and Mean Reversion), a dynamic risk management system, and a rigorous multi-symbol, multi-timeframe evaluation methodology.
 
**Universe tested:** 10 symbols spanning tech (AAPL, MSFT, NVDA), financials (JPM), healthcare (JNJ), energy (XOM), consumer staples (PG, WMT, KO), and consumer discretionary (DIS) — chosen deliberately for a mix of trending and range-bound historical behaviour.
 
**Timeframes tested:** Daily bars (2014–2019, pre-COVID; and 2020–2024, including COVID volatility) and hourly bars (2023–2024).
 
---
 
## Architecture Highlights
 
- **Event-driven design**: a shared `process_signal()` interface in `Portfolio` means the same code path handles both backtesting and (eventually) live paper trading — no duplicated logic between simulation and execution.
- **Pluggable strategy interface**: an abstract `Strategy` base class means new strategies can be added without touching the backtest engine or portfolio logic — genuine separation of concerns.
- **Dynamic risk governor**: position sizing, stop-loss width, and max concurrent positions are controlled by a `RiskGovernor` modeled on a **2-bit saturating counter** (the same design used in CPU branch predictors). Each closed trade's outcome nudges the risk state up or down by one step, saturating at the extremes — providing hysteresis so a single anomalous result doesn't overreact, while sustained performance trends do shift the risk profile. Position size, stop-loss percentage, and max open positions are interpolated continuously across the risk state rather than jumping between arbitrary fixed tiers.
- **Buy-and-hold benchmarking**: every backtest run is compared against simply buying and holding the same symbol over the same period — essential for judging whether the strategies add real value versus just being invested in a rising market.
---
 
## Key Findings
 
### 1. Buy-and-hold outperformed both strategies on every symbol tested
 
Across both the 2014–2019 daily test and the 2023 hourly test, simply buying and holding beat both active strategies on every single symbol — often by a wide margin (e.g. NVDA: ~230–310% buy-and-hold vs. single-digit returns for either strategy).
 
**Interpretation:** this is an expected and well-documented result for simple technical strategies tested during a sustained bull market, not a flaw in the implementation. It highlights an important limitation of momentum/reversion strategies: they tend to under-participate in strong sustained trends, since they're designed to react to short-term price behaviour rather than ride a long-term trend unconditionally.
 
### 2. Mean Reversion consistently produced a much higher win rate than MA Crossover
 
Averaged across all 10 symbols, Mean Reversion's win rate was roughly double MA Crossover's (e.g. 64–68% vs. 34%), and this pattern held across both daily and hourly timeframes — a repeatable, not coincidental, result.
 
**Interpretation:** this is consistent with the theoretical distinction between the two strategy types — trend-following strategies (MA Crossover) typically have lower win rates but rely on a few large winning trades to be profitable, while mean-reversion strategies typically have higher win rates with smaller, more frequent gains. The data confirms this textbook pattern.
 
### 3. Risk-adjusted performance (not just returns) tells a more nuanced story
 
Despite lower absolute returns, both strategies — and Mean Reversion in particular — showed meaningfully lower maximum drawdowns than buy-and-hold in several cases. This suggests their practical value proposition is closer to **capital preservation and reduced volatility** rather than outperformance — a legitimate, real-world characteristic of many risk-managed trading products.
 
### 4. A hypothesis test on the Mean Reversion exit rule — instinct overturned by data
 
**Hypothesis tested:** exiting a mean-reversion trade as soon as price reverts to the rolling mean (rather than waiting for it to swing to the *opposite* Bollinger Band) would produce more frequent, smaller wins that compound favourably over time.
 
**Method:** the two exit rules were compared with the risk governor held constant, isolating the exit rule as the only variable — an important methodological correction after an earlier test accidentally changed two variables at once (the exit rule and the risk governor simultaneously), which made the initial results uninterpretable.
 
**Result:** the original band-to-band exit outperformed the "exit at mean" variant on both average return (1.51% vs. 0.56%) and Sharpe ratio (0.13 vs. 0.08), despite trading roughly 30–40% less often. The "exit at mean" version generated more trades but gave up the second half of the average reversion move, and the extra trade frequency did not compensate for the smaller average win size.
 
**Interpretation:** this was a case where a reasonable-sounding intuition ("smaller, more frequent wins should compound") did not hold up under direct empirical testing. The project's methodology — isolate variables, test hypotheses against out-of-sample data, and let results override intuition — is arguably a more valuable takeaway than either result in isolation.
 
---
 
## Honest Limitations (Acknowledged, Not Hidden)
 
- **No transaction costs modeled yet.** Mean Reversion's higher trade frequency (often 40–70 trades per symbol per year) makes it more exposed to the effect of spread and commission than these results currently reflect. This is a planned next step.
- **Single-strategy, single-asset testing so far.** Combining signals (e.g. requiring agreement between both strategies) or portfolio-level diversification across symbols simultaneously has not yet been tested.
- **No train/test split for parameters.** Strategy parameters (moving average windows, Bollinger Band width) have not yet been optimized on a held-out sample, so there is a risk that any further parameter tuning could overfit to the specific historical periods tested.
- **Backtests assume perfect, instant order fills** at the closing/bar price, which is optimistic relative to real execution.
---
 
## Suggested Next Steps
 
1. Add realistic transaction cost modeling (e.g. a fixed basis-point cost per trade) and re-run the full comparison to see whether Mean Reversion's edge survives realistic costs.
2. Test a train/test parameter split to check for overfitting before finalizing strategy parameters.
3. Wire the system to Alpaca's paper trading API for live (simulated) execution, using the same `process_signal()` interface already built for backtesting.
4. Polish the README with an architecture diagram and the results above, ready to present as a portfolio piece.