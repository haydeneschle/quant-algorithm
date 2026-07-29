"""
Central configuration for the trading bot: API credentials, the
symbol universe to trade, timeframe, backtest window, and strategy
parameters. Everything here is imported by name (`import config`)
rather than passed around as arguments, so changing a setting only
requires editing this one file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Alpaca API credentials ---
# Loaded from a local .env file (never committed — see .gitignore)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # paper trading endpoint only

# --- Trading universe ---
# Deliberately spread across sectors with different historical behaviour,
# rather than a cluster of similar tech names — this matters for testing
# the regime-switching strategy, since it needs both trending and
# range-bound symbols to have something meaningful to switch between.
SYMBOLS = [
    "AAPL",   # Tech - large cap, trending history
    "MSFT",   # Tech - large cap, steadier trend
    "JPM",    # Financials - cyclical, rate-sensitive
    "JNJ",    # Healthcare - defensive, low volatility
    "XOM",    # Energy - cyclical, commodity-driven
    "PG",     # Consumer Staples - very defensive, range-bound
    "WMT",    # Consumer Staples/Retail - steady grower
    "DIS",    # Consumer Discretionary - more volatile, choppier
    "KO",     # Consumer Staples - classic range-bound/mean-reverting
    "NVDA",   # Tech - high growth, high volatility
]

TIMEFRAME = "1Hour"

# Moving average windows, expressed in bars rather than days since
# TIMEFRAME is hourly. US markets trade ~6.5 hours/day, so these
# approximate the same "20 day" / "50 day" windows used on daily bars.
SHORT_WINDOW = 140   # ~20 trading days worth of hourly bars
LONG_WINDOW = 350    # ~50 trading days worth of hourly bars

# --- Backtest settings ---
START_DATE = "2020-01-01"
END_DATE = "2024-01-01"
INITIAL_CAPITAL = 10000.0

# --- Paths ---
CACHE_DIR = "data/cache"