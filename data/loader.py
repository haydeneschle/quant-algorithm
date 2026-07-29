"""
Historical data loading via the Alpaca API, with local CSV caching
so repeated backtests don't re-fetch the same data.
"""

import os
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

import config


def _get_timeframe(tf_str: str) -> TimeFrame:
    """Convert the timeframe string in config.py to Alpaca's TimeFrame object."""
    mapping = {
        "1Min": TimeFrame.Minute,
        "1Hour": TimeFrame.Hour,
        "1Day": TimeFrame.Day,
    }
    return mapping.get(tf_str, TimeFrame.Day)


def _cache_path(symbol: str) -> str:
    """
    Build the cache file path for a given symbol. Includes the
    timeframe in the filename, not just the symbol and date range —
    without this, switching from daily to hourly bars for the same
    symbol/dates would silently load the wrong cached data.
    """
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    return os.path.join(
        config.CACHE_DIR,
        f"{symbol}_{config.TIMEFRAME}_{config.START_DATE}_{config.END_DATE}.csv",
    )


def load_historical_bars(symbol: str, use_cache: bool = True) -> pd.DataFrame:
    """
    Fetch historical bars for a symbol, using a local cache if available.
    Returns a DataFrame indexed by timestamp with columns:
    open, high, low, close, volume (plus trade_count, vwap from Alpaca).
    """
    path = _cache_path(symbol)

    if use_cache and os.path.exists(path):
        return pd.read_csv(path, index_col=0, parse_dates=True)

    client = StockHistoricalDataClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY)

    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=_get_timeframe(config.TIMEFRAME),
        start=config.START_DATE,
        end=config.END_DATE,
    )

    bars = client.get_stock_bars(request)
    df = bars.df

    # Alpaca returns a MultiIndex (symbol, timestamp) even for a single
    # symbol request, so this needs to be flattened before caching.
    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol, level=0)

    df.to_csv(path)
    return df


if __name__ == "__main__":
    # Quick manual smoke test: run `python -m data.loader` from repo root
    # (must be run as a module, not a script, so `import config` resolves).
    data = load_historical_bars(config.SYMBOLS[0])
    print(data.head())
    print(f"\nLoaded {len(data)} bars for {config.SYMBOLS[0]}")