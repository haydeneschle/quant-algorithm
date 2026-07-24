from data.loader import load_historical_bars
from strategy.moving_average import MovingAverageCrossover
from strategy.mean_reversion import MeanReversion
from portfolio.portfolio import Portfolio
from portfolio.risk import RiskGovernor, RiskState
from backtest.engine import BacktestEngine
from backtest.metrics import summary, buy_and_hold_return
import config
from strategy.regime import RegimeSwitchingStrategy

def run_strategy(strategy, data):
    risk_governor = RiskGovernor(starting_state=RiskState.WEAKLY_CONSERVATIVE)
    portfolio = Portfolio(
        initial_capital=config.INITIAL_CAPITAL,
        risk_governor=risk_governor,
    )
    engine = BacktestEngine(data=data, strategy=strategy, portfolio=portfolio)
    final_portfolio = engine.run()
    return summary(final_portfolio, config.INITIAL_CAPITAL)


def print_comparison(results: dict, benchmarks: dict):
    metrics = ["total_return_pct", "sharpe_ratio", "max_drawdown_pct", "win_rate_pct", "num_trades"]
    col_width = 16
    header = f"{'Symbol':<8}{'Strategy':<16}" + "".join(f"{m:>{col_width}}" for m in metrics) + f"{'buy_hold_pct':>{col_width}}"
    print("\n" + header)
    print("-" * len(header))

    for symbol, strat_results in results.items():
        for strat_name, metrics_dict in strat_results.items():
            row = f"{symbol:<8}{strat_name:<16}"
            for m in metrics:
                row += f"{metrics_dict[m]:>{col_width}.2f}"
            row += f"{benchmarks[symbol]:>{col_width}.2f}"
            print(row)


def print_aggregate_summary(results: dict, benchmarks: dict):
    strategy_names = list(next(iter(results.values())).keys())
    print("\n=== Aggregate Summary (averaged across all symbols) ===")
    col_width = 18
    metrics = ["total_return_pct", "sharpe_ratio", "max_drawdown_pct", "win_rate_pct"]

    header = f"{'Strategy':<16}" + "".join(f"{m:>{col_width}}" for m in metrics)
    print(header)
    print("-" * len(header))

    for strat_name in strategy_names:
        avg_metrics = {}
        for m in metrics:
            values = [results[symbol][strat_name][m] for symbol in results]
            avg_metrics[m] = sum(values) / len(values)

        row = f"{strat_name:<16}"
        for m in metrics:
            row += f"{avg_metrics[m]:>{col_width}.2f}"
        print(row)

    avg_benchmark = sum(benchmarks.values()) / len(benchmarks)
    print(f"\nAverage buy-and-hold return across all symbols: {avg_benchmark:.2f}%")


def main():
    strategies = {
        "MA Crossover": lambda: MovingAverageCrossover(
            short_window=config.SHORT_WINDOW,
            long_window=config.LONG_WINDOW,
        ),
        "Mean Reversion": lambda: MeanReversion(),
        "Regime Switching": lambda: RegimeSwitchingStrategy(),
    }

    results = {}
    benchmarks = {}

    for symbol in config.SYMBOLS:
        data = load_historical_bars(symbol)
        data.attrs["symbol"] = symbol

        benchmarks[symbol] = buy_and_hold_return(data)

        results[symbol] = {}
        for name, strategy_factory in strategies.items():
            strategy = strategy_factory()
            results[symbol][name] = run_strategy(strategy, data)

    print(f"\n=== Strategy Comparison: {config.START_DATE} to {config.END_DATE} ===")
    print_comparison(results, benchmarks)
    print_aggregate_summary(results, benchmarks)


if __name__ == "__main__":
    main()