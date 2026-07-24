import os
from dotenv import load_dotenv

load_dotenv()

# Alpaca API credential 
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

# Set of stocks
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

# Roughly 6.5 trading hours/day in US markets → ~1 bar per hour
SHORT_WINDOW = 140   # ~20 trading days worth of hourly bars
LONG_WINDOW = 350    # ~50 trading days worth of hourly bars

# Backtest settings 
START_DATE = "2023-01-01"
END_DATE = "2024-01-01"
INITIAL_CAPITAL = 10000.0

# Risk management
MAX_POSITION_SIZE = 0.1 # max 10% of captial per position
STOP_LOSS_PCT = 0.05 # 5% stop loss

# Paths 
CACHE_DIR = "data/cache"