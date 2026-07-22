import os
from dotenv import load_dotenv

load_dotenv()

# Alpaca API credential 
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

# Set of stocks
SYMBOLS = ["APPL"] # expandable
TIMEFRAME = "1Day" # alterable to 1min...

# Backtest settings 
START_DATE = "2023-01-01"
END_DATE = "2024-01-01"
INITIAL_CAPITAL = 10000.0

# Strategy parameters
SHORT_WINDOW = 20 # short moving average positon
LONG_WINDOW = 50 # long moving average position

# Risk management
MAX_POSITION_SIZE = 0.1 # max 10% of captial per position
STOP_LOSS_PCT = 0.05 # 5% stop loss

# Paths 
CACHE_DIR = "data/cache"