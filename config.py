INITIAL_CAPITAL = 1_00_00_000
ANNUAL_WITHDRAWAL = 4_00_000
DEFAULT_EMA = 220
DEFAULT_STOP_LOSS = 0.0
DEFAULT_TRANSACTION_COST = 0.0
DEFAULT_REBALANCING = "monthly"
MAX_STOCKS = 5

PRELOADED_DATASETS = {
    "HDFC Balanced Advantage": "data/HDFC_Balanced_Advantage_monthly.csv",
    "NIFTYBEES": None,
}

STRATEGY_RULES = {
    "momentum": "Buy top performing stocks based on lookback period returns. Hold for rebalancing period, then rotate to new top performers.",
    "ath_breakout": "Enter when price breaks above all-time high with confirmation. Exit when price falls below entry or hits stop loss.",
    "moving_average": "Enter when fast EMA crosses above slow EMA. Exit on reverse crossover or stop loss.",
    "withdrawal": "Invest capital, withdraw fixed amount at end of each year. Track portfolio survival and growth.",
}

COLORS = {
    "primary": "#1f77b4",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "light_bg": "#ffffff",
    "dark_bg": "#0e1117",
    "dark_surface": "#1e1e1e",
}

DATA_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]
REQUIRED_COLUMNS = ["Date", "Close"]