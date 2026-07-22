import os
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

import config 

def _get_timeframe(tr_str : str) -> TimeFrame:
    """
    Convert config string to Alpaca TimeFrame object
    """
    mapping = {
        "1Min": TimeFrame.Minute,
        "1Hour": TimeFrame.Hour,
        "1Day": TimeFrame.Day,
    }
    return mapping.get(tf_str, TimeFrame.Day)

def _cache_path(symbol: str) -> str:
    os.makedirs(config.CACHE_DIR, exist_ok = True)
    return os.path.join(config.CACHE_DIR, f"{symbol}_{config.START_DATE}_{config.END_DATE}.csv")

def load_historical_bars(symbol: str, use_cache: bool = True) -> pd.DataFrame:
    """
    Fetch historical daily bars for a symbol, using a local cache if available.
    Returns a DataFrame indexed from timestamp with columns: open, high, low, close, volume.
    """

    path = _cahce_path(symbol)

    if use_cache and os.path.exists(path):
        return pd.read_csv(path, index_col = 0, parse_dates = True)

    client = StockHistoricalDataClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY)

    request = StockBarsRequest(
        symbol_or_symbols = symbol,
        timeframe = _get_timeframe(config.TIMEFRAME),
        start = config.START_DATE,
        end = config.END_DATE,
    )

    bars = client.get_stock_bars(request)
    df = bars.df

    # Alpaca returns MultiIndex (symbol, timestamp) when using symbol_or_symbols as a list
    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol, level = 0)

    df.to_csv(path)
    return df