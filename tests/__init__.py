"""
Test Suite for MT5 Trading Bot
Unit tests for critical bot components.
"""

__version__ = "1.0.0"

# Test configuration
TEST_SYMBOL = "EURUSD"
TEST_LOT_SIZE = 0.01
TEST_BALANCE = 10000.0
TEST_RISK_PERCENT = 1.0

# Mock data for testing
MOCK_ACCOUNT_INFO = {
    'login': 12345,
    'balance': TEST_BALANCE,
    'equity': TEST_BALANCE,
    'margin': 0.0,
    'margin_free': TEST_BALANCE,
    'margin_level': 0.0,
    'currency': 'USD',
    'leverage': 100,
    'company': 'Test Broker',
    'server': 'Test-Server',
    'trade_allowed': True,
    'trade_expert': True
}

MOCK_SYMBOL_INFO = {
    'name': TEST_SYMBOL,
    'digits': 5,
    'point': 0.00001,
    'trade_mode': 0,
    'volume_min': 0.01,
    'volume_max': 100.0,
    'volume_step': 0.01,
    'currency_base': 'EUR',
    'currency_profit': 'USD',
    'currency_margin': 'EUR',
    'visible': True,
    'trade_tick_value': 1.0,
    'trade_tick_size': 0.00001
}

MOCK_TICK_DATA = {
    'symbol': TEST_SYMBOL,
    'bid': 1.08500,
    'ask': 1.08520,
    'last': 1.08510,
    'volume': 100,
    'time': 1640995200,  # 2022-01-01 00:00:00
    'spread': 0.0002
}
