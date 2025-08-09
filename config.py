"""
Configuration module for MT5 Trading Bot
Contains all constants, settings, and configuration parameters.
"""

import os
from typing import Dict, Any, List, Tuple

# === SECURITY CONFIGURATION ===
# Get sensitive data from environment variables for security
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your_telegram_bot_token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id")

# === CONNECTION CONFIGURATION ===
MAX_CONNECTION_ATTEMPTS = 5
MAX_CONSECUTIVE_FAILURES = 10
DEFAULT_TIMEOUT_SECONDS = 10
MAX_SYMBOL_TEST_ATTEMPTS = 3
CONNECTION_RETRY_DELAY = 3  # seconds

# === GUI CONFIGURATION ===
GUI_UPDATE_INTERVAL = 1500  # milliseconds

# === TRADING CONFIGURATION ===
BOT_LOOP_INTERVALS = {
    "HFT": 0.5,
    "Scalping": 1.0,
    "Intraday": 2.0,
    "Arbitrage": 2.0
}

# Default trading parameters
DEFAULT_RISK_PERCENT = 1.0
DEFAULT_MAX_POSITIONS = 10
MAX_POSITIONS = 10  # Legacy constant for compatibility
DEFAULT_MAGIC_NUMBER = 12345
DEFAULT_DEVIATION = 20

# === RISK MANAGEMENT CONFIGURATION ===
MAX_LOSS_STREAK = 3
MAX_DRAWDOWN = 0.05  # 5%
PROFIT_TARGET = 0.10  # 10%
DAILY_MAX_LOSS = 0.05  # 5%
TRAILING_STOP_ENABLED = False

# === TRADING SESSIONS ===
TRADING_SESSIONS = {
    "Asia": {
        "start": "21:00",
        "end": "06:00",
        "timezone": "UTC",
        "active": True,
        "volatility": "medium",
        "preferred_pairs": ["USDJPY", "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY"]
    },
    "London": {
        "start": "07:00",
        "end": "15:00",
        "timezone": "UTC",
        "active": True,
        "volatility": "high",
        "preferred_pairs": ["EURUSD", "GBPUSD", "EURGBP", "EURJPY", "GBPJPY"]
    },
    "New_York": {
        "start": "15:00",
        "end": "21:00",
        "timezone": "UTC",
        "active": True,
        "volatility": "high",
        "preferred_pairs": ["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "AUDUSD"]
    },
    "Overlap_London_NY": {
        "start": "15:00",
        "end": "17:00",
        "timezone": "UTC",
        "active": True,
        "volatility": "very_high",
        "preferred_pairs": ["EURUSD", "GBPUSD", "USDCAD"]
    }
}

# === SESSION SETTINGS ===
SESSION_SETTINGS = {
    "Asia": {
        "max_spread_multiplier": 1.5,
        "volatility_filter": 0.7,
        "trading_intensity": "conservative",
        "lot_multiplier": 0.8,
        "tp_multiplier": 1.0,
        "sl_multiplier": 1.2
    },
    "London": {
        "max_spread_multiplier": 1.2,
        "volatility_filter": 1.0,
        "trading_intensity": "aggressive",
        "lot_multiplier": 1.0,
        "tp_multiplier": 1.0,
        "sl_multiplier": 1.0
    },
    "New_York": {
        "max_spread_multiplier": 1.0,
        "volatility_filter": 1.2,
        "trading_intensity": "aggressive",
        "lot_multiplier": 1.2,
        "tp_multiplier": 1.1,
        "sl_multiplier": 0.9
    },
    "Overlap_London_NY": {
        "max_spread_multiplier": 0.8,
        "volatility_filter": 1.5,
        "trading_intensity": "very_aggressive",
        "lot_multiplier": 1.5,
        "tp_multiplier": 1.2,
        "sl_multiplier": 0.8
    }
}

# === STRATEGY CONFIGURATION ===
STRATEGY_DEFAULTS = {
    "HFT": {
        "tp_pips": 3,
        "sl_pips": 2,
        "lot_size": 0.01,
        "indicators": ["EMA", "RSI"]
    },
    "Scalping": {
        "tp_pips": 8,
        "sl_pips": 5,
        "lot_size": 0.05,
        "indicators": ["EMA", "RSI", "MACD"]
    },
    "Intraday": {
        "tp_pips": 25,
        "sl_pips": 15,
        "lot_size": 0.1,
        "indicators": ["EMA", "RSI", "MACD", "ATR"]
    },
    "Arbitrage": {
        "tp_pips": 1,
        "sl_pips": 0.5,
        "lot_size": 0.01,
        "indicators": ["Spread"]
    }
}

# === SYMBOL CONFIGURATION ===
POPULAR_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
    "EURJPY", "GBPJPY", "EURGBP", "AUDCAD", "GBPCAD", "AUDNZD",
    "XAUUSD", "XAGUSD", "USOIL", "UKBRENT"
]

GOLD_SYMBOL_VARIATIONS = [
    "XAUUSD", "GOLD", "XAU", "XAUUSD.m", "GOLD.m", "XAU.m",
    "XAUUSD.raw", "GOLD.raw", "XAU.raw", "XAUUSD_m", "GOLD_m"
]

# === SPREAD THRESHOLDS ===
SPREAD_THRESHOLDS = {
    "forex_major": 3.0,
    "forex_minor": 5.0,
    "forex_exotic": 10.0,
    "jpy_pairs": 2.5,
    "gold": 5.0,
    "silver": 8.0,
    "oil": 4.0,
    "crypto": 50.0,
    "indices": 10.0
}

# === NEWS FILTER CONFIGURATION ===
HIGH_IMPACT_NEWS_TIMES = [
    # Daily major news (UTC hours)
    (8, 30, 9, 30),   # European session major news
    (12, 30, 14, 30), # US session major news (NFP, CPI, FOMC, etc)
    (16, 0, 16, 30),  # London Fix
]

# Weekly specific news times
WEEKLY_NEWS_TIMES = {
    2: [(13, 0, 14, 0)],    # Wednesday FOMC minutes
    4: [(12, 30, 15, 0)]    # Friday NFP + major data
}

# === LOGGING CONFIGURATION ===
LOG_LEVELS = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4
}

LOG_FORMAT = "[{timestamp}] {level}: {message}"
LOG_DIR = "logs"
LOG_FILE_PREFIX = "trading_bot"
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_LOG_FILES = 5

# === INDICATOR CONFIGURATION ===
INDICATOR_PERIODS = {
    "EMA_fast": 12,
    "EMA_slow": 26,
    "RSI": 14,
    "MACD_fast": 12,
    "MACD_slow": 26,
    "MACD_signal": 9,
    "ATR": 14,
    "BB": 20,
    "Stochastic_K": 14,
    "Stochastic_D": 3
}

# === NOTIFICATION CONFIGURATION ===
NOTIFICATION_EVENTS = [
    "bot_started",
    "bot_stopped",
    "order_opened",
    "order_closed",
    "connection_lost",
    "emergency_stop",
    "profit_target_reached",
    "max_loss_reached"
]

# === FILE PATHS ===
CONFIG_DIR = "config"
DATA_DIR = "data"
BACKUP_DIR = "backups"
TEMP_DIR = "temp"

# === VALIDATION RULES ===
MIN_LOT_SIZE = 0.01
MAX_LOT_SIZE = 100.0
MIN_RISK_PERCENT = 0.1
MAX_RISK_PERCENT = 10.0
MIN_TP_PIPS = 1
MAX_TP_PIPS = 1000
MIN_SL_PIPS = 1
MAX_SL_PIPS = 500

# === PERFORMANCE MONITORING ===
PERFORMANCE_METRICS = [
    "total_trades",
    "winning_trades",
    "losing_trades",
    "win_rate",
    "total_profit",
    "average_profit",
    "max_drawdown",
    "profit_factor",
    "sharpe_ratio"
]

# === API RATE LIMITS ===
MT5_API_RATE_LIMIT = 10  # requests per second
TELEGRAM_API_RATE_LIMIT = 1  # messages per second
NEWS_API_RATE_LIMIT = 100  # requests per day

# === CURRENCY PAIRS CLASSIFICATION ===
FOREX_MAJOR = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
FOREX_MINOR = ["EURJPY", "GBPJPY", "EURGBP", "AUDCAD", "GBPCAD", "AUDNZD", "NZDCAD"]
FOREX_EXOTIC = ["USDTRY", "USDZAR", "USDMXN", "USDHUF", "USDPLN", "USDCZK"]
PRECIOUS_METALS = ["XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD"]
COMMODITIES = ["USOIL", "UKBRENT", "NATGAS", "COPPER"]
INDICES = ["US30", "US500", "NAS100", "GER30", "UK100", "FRA40", "AUS200"]
CRYPTOCURRENCIES = ["BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "BCHUSD"]
