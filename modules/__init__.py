"""
MT5 Trading Bot Modules Package
This package contains all the modular components of the trading bot.
"""

__version__ = "1.0.0"
__author__ = "MT5 Trading Bot Team"

# Package metadata
PACKAGE_NAME = "mt5_trading_bot_modules"
DESCRIPTION = "Modular components for MT5 automated trading bot"

# Import main classes for easy access
from .connection import MT5Connection
from .logging_utils import BotLogger
from .account import AccountManager
from .symbols import SymbolManager
from .risk import RiskManager
from .strategy import StrategyManager
from .orders import OrderManager
from .sessions import SessionManager
from .indicators import IndicatorCalculator
from .news_filter import NewsFilter
from .gui import TradingBotGUI
from .utils import cleanup_resources, validate_numeric_input, validate_string_input

__all__ = [
    "MT5Connection",
    "BotLogger", 
    "AccountManager",
    "SymbolManager",
    "RiskManager",
    "StrategyManager",
    "OrderManager",
    "SessionManager",
    "IndicatorCalculator",
    "NewsFilter",
    "TradingBotGUI",
    "cleanup_resources",
    "validate_numeric_input",
    "validate_string_input"
]
