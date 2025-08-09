"""
Unit tests for Symbol Management Module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.symbols import SymbolManager
from modules.logging_utils import BotLogger
from tests import MOCK_SYMBOL_INFO, MOCK_TICK_DATA, TEST_SYMBOL


class MockMT5Symbol:
    """Mock MT5 symbol object."""
    def __init__(self, name, visible=True):
        self.name = name
        self.visible = visible


class MockMT5Connection:
    """Mock MT5 connection object."""
    def __init__(self):
        self.mt5 = Mock()
        
    def check_connection(self):
        return True


class TestSymbolManager(unittest.TestCase):
    """Test cases for SymbolManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = Mock(spec=BotLogger)
        self.connection = MockMT5Connection()
        
        # Configure MT5 mock
        self.connection.mt5.symbols_get.return_value = [
            MockMT5Symbol("EURUSD", True),
            MockMT5Symbol("GBPUSD", True),
            MockMT5Symbol("USDJPY", True),
            MockMT5Symbol("XAUUSD", False)  # Not visible
        ]
        
        self.symbol_manager = SymbolManager(self.logger, self.connection)
    
    def test_get_symbols(self):
        """Test getting list of available symbols."""
        symbols = self.symbol_manager.get_symbols()
        
        # Should only return visible symbols
        expected_symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        self.assertEqual(symbols, expected_symbols)
    
    def test_get_symbols_no_connection(self):
        """Test getting symbols with no connection."""
        self.connection.check_connection = Mock(return_value=False)
        
        symbols = self.symbol_manager.get_symbols()
        
        self.assertEqual(symbols, [])
    
    def test_get_symbol_suggestions(self):
        """Test getting symbol suggestions."""
        suggestions = self.symbol_manager.get_symbol_suggestions()
        
        # Should return popular symbols from config
        self.assertIsInstance(suggestions, list)
        self.assertIn("EURUSD", suggestions)
        self.assertIn("GBPUSD", suggestions)
    
    def test_validate_and_activate_symbol_success(self):
        """Test successful symbol validation and activation."""
        # Mock successful symbol validation
        self.connection.mt5.symbol_info.return_value = Mock(
            visible=True,
            trade_mode=0,  # Trading allowed
            digits=5,
            point=0.00001
        )
        self.connection.mt5.symbol_info_tick.return_value = Mock(
            bid=1.08500,
            ask=1.08520
        )
        
        with patch.object(self.symbol_manager, '_test_symbol', return_value=True):
            result = self.symbol_manager.validate_and_activate_symbol(TEST_SYMBOL)
            
        self.assertTrue(result)
    
    def test_validate_and_activate_symbol_failure(self):
        """Test failed symbol validation."""
        # Mock failed symbol validation
        self.connection.mt5.symbol_info.return_value = None
        
        with patch.object(self.symbol_manager, '_test_symbol', return_value=False):
            result = self.symbol_manager.validate_and_activate_symbol("INVALID")
            
        self.assertFalse(result)
    
    def test_validate_and_activate_symbol_with_variations(self):
        """Test symbol validation with variations."""
        # First attempt fails, second succeeds
        def mock_test_symbol(symbol):
            return symbol == "EURUSD.m"
        
        with patch.object(self.symbol_manager, '_test_symbol', side_effect=mock_test_symbol):
            result = self.symbol_manager.validate_and_activate_symbol("EURUSD")
            
        self.assertTrue(result)
    
    def test_generate_symbol_variations(self):
        """Test symbol variation generation."""
        variations = self.symbol_manager._generate_symbol_variations("EURUSD")
        
        expected_variations = [
            "EURUSD",
            "EURUSD.m",
            "EURUSD.raw",
            "EURUSD_m",
            "EURUSD-m",
            "EURUSD",  # No change for alphanumeric
            "EURUSD",  # No change for no special chars
            "EUR/USD",
            "EUR-USD"
        ]
        
        # Check that key variations are present
        self.assertIn("EURUSD", variations)
        self.assertIn("EURUSD.m", variations)
        self.assertIn("EUR/USD", variations)
    
    def test_test_symbol_success(self):
        """Test successful symbol testing."""
        # Mock successful symbol info and tick
        symbol_info_mock = Mock(
            visible=True,
            trade_mode=0,
            point=0.00001
        )
        tick_mock = Mock(bid=1.08500, ask=1.08520)
        
        self.connection.mt5.symbol_info.return_value = symbol_info_mock
        self.connection.mt5.symbol_select.return_value = True
        self.connection.mt5.symbol_info_tick.return_value = tick_mock
        
        with patch.object(self.symbol_manager, '_is_spread_acceptable', return_value=True):
            result = self.symbol_manager._test_symbol(TEST_SYMBOL)
            
        self.assertTrue(result)
    
    def test_test_symbol_no_symbol_info(self):
        """Test symbol testing with no symbol info."""
        self.connection.mt5.symbol_info.return_value = None
        
        result = self.symbol_manager._test_symbol("INVALID")
        
        self.assertFalse(result)
    
    def test_test_symbol_trading_disabled(self):
        """Test symbol testing with trading disabled."""
        symbol_info_mock = Mock(
            visible=True,
            trade_mode=1,  # Trading disabled
            point=0.00001
        )
        
        self.connection.mt5.symbol_info.return_value = symbol_info_mock
        self.connection.mt5.symbol_info_tick.return_value = Mock(bid=1.08500, ask=1.08520)
        
        result = self.symbol_manager._test_symbol(TEST_SYMBOL)
        
        self.assertFalse(result)
    
    def test_is_spread_acceptable_forex_major(self):
        """Test spread acceptance for forex major pairs."""
        spread_pips = 2.0  # Acceptable for major pairs
        
        result = self.symbol_manager._is_spread_acceptable("EURUSD", spread_pips)
        
        self.assertTrue(result)
    
    def test_is_spread_acceptable_too_wide(self):
        """Test spread rejection for too wide spreads."""
        spread_pips = 10.0  # Too wide for major pairs
        
        result = self.symbol_manager._is_spread_acceptable("EURUSD", spread_pips)
        
        self.assertFalse(result)
    
    def test_is_spread_acceptable_jpy_pairs(self):
        """Test spread acceptance for JPY pairs."""
        spread_pips = 2.0  # Acceptable for JPY pairs
        
        result = self.symbol_manager._is_spread_acceptable("USDJPY", spread_pips)
        
        self.assertTrue(result)
    
    def test_is_spread_acceptable_gold(self):
        """Test spread acceptance for gold."""
        spread_pips = 4.0  # Acceptable for gold
        
        result = self.symbol_manager._is_spread_acceptable("XAUUSD", spread_pips)
        
        self.assertTrue(result)
    
    def test_detect_gold_symbol(self):
        """Test gold symbol detection."""
        with patch.object(self.symbol_manager, '_test_symbol') as mock_test:
            # First two variations fail, third succeeds
            mock_test.side_effect = [False, False, True]
            
            result = self.symbol_manager.detect_gold_symbol()
            
            self.assertIsNotNone(result)
    
    def test_detect_gold_symbol_not_found(self):
        """Test gold symbol detection when no valid symbol found."""
        with patch.object(self.symbol_manager, '_test_symbol', return_value=False):
            result = self.symbol_manager.detect_gold_symbol()
            
            self.assertIsNone(result)
    
    def test_get_symbol_info(self):
        """Test getting symbol information."""
        # Mock symbol info
        symbol_info_mock = Mock(
            name=TEST_SYMBOL,
            description="Euro vs US Dollar",
            digits=5,
            point=0.00001,
            trade_mode=0,
            volume_min=0.01,
            volume_max=100.0,
            volume_step=0.01,
            currency_base="EUR",
            currency_profit="USD",
            currency_margin="EUR",
            visible=True,
            trade_tick_value=1.0,
            trade_tick_size=0.00001
        )
        
        tick_mock = Mock(
            bid=1.08500,
            ask=1.08520,
            time=1640995200
        )
        
        self.connection.mt5.symbol_info.return_value = symbol_info_mock
        self.connection.mt5.symbol_info_tick.return_value = tick_mock
        
        info = self.symbol_manager.get_symbol_info(TEST_SYMBOL)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], TEST_SYMBOL)
        self.assertEqual(info['digits'], 5)
        self.assertEqual(info['bid'], 1.08500)
        self.assertEqual(info['ask'], 1.08520)
        self.assertAlmostEqual(info['spread'], 2.0, places=1)  # (1.08520 - 1.08500) / 0.00001
    
    def test_get_symbol_info_no_symbol(self):
        """Test getting symbol info for non-existent symbol."""
        self.connection.mt5.symbol_info.return_value = None
        
        info = self.symbol_manager.get_symbol_info("INVALID")
        
        self.assertIsNone(info)
    
    def test_get_tick_data(self):
        """Test getting tick data."""
        tick_mock = Mock(
            bid=1.08500,
            ask=1.08520,
            last=1.08510,
            volume=100,
            time=1640995200
        )
        
        self.connection.mt5.symbol_info_tick.return_value = tick_mock
        
        tick_data = self.symbol_manager.get_tick_data(TEST_SYMBOL)
        
        self.assertIsNotNone(tick_data)
        self.assertEqual(tick_data['symbol'], TEST_SYMBOL)
        self.assertEqual(tick_data['bid'], 1.08500)
        self.assertEqual(tick_data['ask'], 1.08520)
        self.assertAlmostEqual(tick_data['spread'], 0.0002, places=4)
    
    def test_get_tick_data_with_retries(self):
        """Test getting tick data with retry mechanism."""
        # First call returns None, second call succeeds
        tick_mock = Mock(
            bid=1.08500,
            ask=1.08520,
            last=1.08510,
            volume=100,
            time=1640995200
        )
        
        self.connection.mt5.symbol_info_tick.side_effect = [None, tick_mock]
        
        tick_data = self.symbol_manager.get_tick_data(TEST_SYMBOL, retries=2)
        
        self.assertIsNotNone(tick_data)
        self.assertEqual(tick_data['bid'], 1.08500)
    
    def test_get_tick_data_failure(self):
        """Test getting tick data failure after retries."""
        self.connection.mt5.symbol_info_tick.return_value = None
        
        tick_data = self.symbol_manager.get_tick_data(TEST_SYMBOL, retries=3)
        
        self.assertIsNone(tick_data)
    
    def test_is_market_open(self):
        """Test market open detection."""
        import datetime
        
        # Mock recent tick data
        tick_mock = Mock(
            bid=1.08500,
            ask=1.08520,
            time=datetime.datetime.now().timestamp() - 60  # 1 minute ago
        )
        
        with patch.object(self.symbol_manager, 'get_tick_data', return_value={
            'time': tick_mock.time,
            'bid': tick_mock.bid,
            'ask': tick_mock.ask
        }):
            result = self.symbol_manager.is_market_open(TEST_SYMBOL)
            
        self.assertTrue(result)
    
    def test_is_market_closed(self):
        """Test market closed detection."""
        import datetime
        
        # Mock old tick data
        old_time = datetime.datetime.now().timestamp() - 600  # 10 minutes ago
        
        with patch.object(self.symbol_manager, 'get_tick_data', return_value={
            'time': old_time,
            'bid': 1.08500,
            'ask': 1.08520
        }):
            result = self.symbol_manager.is_market_open(TEST_SYMBOL)
            
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
