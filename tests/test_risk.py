"""
Unit tests for Risk Management Module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.risk import RiskManager
from modules.logging_utils import BotLogger
from tests import MOCK_ACCOUNT_INFO, MOCK_SYMBOL_INFO, MOCK_TICK_DATA, TEST_SYMBOL, TEST_LOT_SIZE, TEST_BALANCE


class TestRiskManager(unittest.TestCase):
    """Test cases for RiskManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = Mock(spec=BotLogger)
        self.symbol_manager = Mock()
        self.account_manager = Mock()
        
        # Configure account manager
        self.account_manager.account_info = MOCK_ACCOUNT_INFO
        self.account_manager.get_balance.return_value = TEST_BALANCE
        self.account_manager.get_currency_conversion_rate.return_value = 1.0
        
        # Configure symbol manager
        self.symbol_manager.get_symbol_info.return_value = MOCK_SYMBOL_INFO
        
        self.risk_manager = RiskManager(self.logger, self.symbol_manager, self.account_manager)
    
    def test_calculate_pip_value_forex_major(self):
        """Test pip value calculation for forex major pairs."""
        pip_value = self.risk_manager.calculate_pip_value(TEST_SYMBOL, TEST_LOT_SIZE)
        
        # For EURUSD, 1 pip = 0.00001 * 100000 * 0.01 = 0.01 USD
        expected_pip_value = 0.01
        self.assertAlmostEqual(pip_value, expected_pip_value, places=4)
    
    def test_calculate_pip_value_with_tick_value(self):
        """Test pip value calculation using tick value method."""
        # Mock symbol info with tick value
        symbol_info = MOCK_SYMBOL_INFO.copy()
        symbol_info['trade_tick_value'] = 1.0
        symbol_info['trade_tick_size'] = 0.00001
        self.symbol_manager.get_symbol_info.return_value = symbol_info
        
        pip_value = self.risk_manager.calculate_pip_value(TEST_SYMBOL, 1.0)
        
        # tick_value / tick_size * point * lot_size = 1.0 / 0.00001 * 0.00001 * 1.0 = 1.0
        expected_pip_value = 1.0
        self.assertAlmostEqual(pip_value, expected_pip_value, places=4)
    
    def test_calculate_auto_lot_size(self):
        """Test automatic lot size calculation."""
        sl_pips = 20.0
        risk_percent = 1.0
        
        # Mock pip value calculation
        with patch.object(self.risk_manager, 'calculate_pip_value', return_value=1.0):
            lot_size = self.risk_manager.calculate_auto_lot_size(TEST_SYMBOL, sl_pips, risk_percent)
            
            # Expected: (balance * risk_percent / 100) / (sl_pips * pip_value)
            # (10000 * 1 / 100) / (20 * 1) = 100 / 20 = 5.0
            # But limited by volume_max (100.0)
            expected_lot_size = 5.0
            self.assertAlmostEqual(lot_size, expected_lot_size, places=2)
    
    def test_calculate_auto_lot_size_with_constraints(self):
        """Test auto lot size with symbol constraints."""
        sl_pips = 10.0
        risk_percent = 0.1  # Very small risk
        
        with patch.object(self.risk_manager, 'calculate_pip_value', return_value=1.0):
            lot_size = self.risk_manager.calculate_auto_lot_size(TEST_SYMBOL, sl_pips, risk_percent)
            
            # Should be limited by volume_min (0.01)
            expected_lot_size = 0.01
            self.assertAlmostEqual(lot_size, expected_lot_size, places=2)
    
    def test_parse_tp_sl_input_pips(self):
        """Test TP/SL parsing with pips unit."""
        result = self.risk_manager.parse_tp_sl_input(
            input_value="20",
            unit="pips",
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            current_price=1.08500,
            order_type="BUY",
            is_tp=True
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['pips'], 20.0)
        self.assertEqual(result['unit'], 'pips')
        # For BUY TP: price + pips = 1.08500 + (20 * 0.00001) = 1.08520
        expected_price = 1.08500 + (20 * 0.00001)
        self.assertAlmostEqual(result['price_level'], expected_price, places=5)
    
    def test_parse_tp_sl_input_price(self):
        """Test TP/SL parsing with price unit."""
        target_price = 1.08600
        
        result = self.risk_manager.parse_tp_sl_input(
            input_value=str(target_price),
            unit="price",
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            current_price=1.08500,
            order_type="BUY",
            is_tp=True
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['price_level'], target_price)
        # Pips should be calculated as price difference / point
        expected_pips = (target_price - 1.08500) / 0.00001
        self.assertAlmostEqual(result['pips'], expected_pips, places=1)
    
    def test_parse_tp_sl_input_percentage(self):
        """Test TP/SL parsing with percentage unit."""
        with patch.object(self.risk_manager, 'calculate_pip_value', return_value=1.0):
            result = self.risk_manager.parse_tp_sl_input(
                input_value="1.0",  # 1% of balance
                unit="%",
                symbol=TEST_SYMBOL,
                lot_size=TEST_LOT_SIZE,
                current_price=1.08500,
                order_type="BUY",
                is_tp=True
            )
            
            self.assertIsNotNone(result)
            # 1% of 10000 = 100, with pip_value=1.0, required_pips = 100
            expected_pips = 100.0
            self.assertAlmostEqual(result['pips'], expected_pips, places=1)
    
    def test_validate_tp_sl_levels_buy_order(self):
        """Test TP/SL level validation for BUY order."""
        current_price = 1.08500
        tp_price = 1.08600  # Above current price (correct for BUY)
        sl_price = 1.08400  # Below current price (correct for BUY)
        
        # Mock symbol info with stop level
        symbol_info = MOCK_SYMBOL_INFO.copy()
        self.symbol_manager.get_symbol_info.return_value = symbol_info
        
        is_valid = self.risk_manager.validate_tp_sl_levels(
            TEST_SYMBOL, tp_price, sl_price, "BUY", current_price
        )
        
        self.assertTrue(is_valid)
    
    def test_validate_tp_sl_levels_sell_order(self):
        """Test TP/SL level validation for SELL order."""
        current_price = 1.08500
        tp_price = 1.08400  # Below current price (correct for SELL)
        sl_price = 1.08600  # Above current price (correct for SELL)
        
        is_valid = self.risk_manager.validate_tp_sl_levels(
            TEST_SYMBOL, tp_price, sl_price, "SELL", current_price
        )
        
        self.assertTrue(is_valid)
    
    def test_validate_tp_sl_levels_invalid_buy(self):
        """Test TP/SL validation with invalid levels for BUY."""
        current_price = 1.08500
        tp_price = 1.08400  # Below current price (incorrect for BUY)
        sl_price = 1.08600  # Above current price (incorrect for BUY)
        
        is_valid = self.risk_manager.validate_tp_sl_levels(
            TEST_SYMBOL, tp_price, sl_price, "BUY", current_price
        )
        
        self.assertFalse(is_valid)
    
    def test_calculate_risk_reward_ratio(self):
        """Test risk-reward ratio calculation."""
        tp_pips = 30.0
        sl_pips = 15.0
        
        ratio = self.risk_manager.calculate_risk_reward_ratio(tp_pips, sl_pips)
        
        expected_ratio = 30.0 / 15.0  # 2.0
        self.assertEqual(ratio, expected_ratio)
    
    def test_calculate_risk_reward_ratio_zero_sl(self):
        """Test risk-reward ratio with zero stop loss."""
        tp_pips = 30.0
        sl_pips = 0.0
        
        ratio = self.risk_manager.calculate_risk_reward_ratio(tp_pips, sl_pips)
        
        self.assertEqual(ratio, 0.0)
    
    def test_validate_position_size(self):
        """Test position size validation."""
        lot_size = 0.1
        
        # Mock margin calculation
        self.account_manager.calculate_margin_requirement.return_value = 100.0
        self.account_manager.get_free_margin.return_value = 5000.0
        
        is_valid = self.risk_manager.validate_position_size(TEST_SYMBOL, lot_size)
        
        self.assertTrue(is_valid)
    
    def test_validate_position_size_insufficient_margin(self):
        """Test position size validation with insufficient margin."""
        lot_size = 10.0
        
        # Mock high margin requirement
        self.account_manager.calculate_margin_requirement.return_value = 5000.0
        self.account_manager.get_free_margin.return_value = 1000.0  # Insufficient
        
        is_valid = self.risk_manager.validate_position_size(TEST_SYMBOL, lot_size)
        
        self.assertFalse(is_valid)
    
    def test_get_risk_summary(self):
        """Test risk summary generation."""
        with patch.object(self.risk_manager, 'calculate_pip_value', return_value=1.0):
            summary = self.risk_manager.get_risk_summary(
                symbol=TEST_SYMBOL,
                lot_size=0.1,
                sl_pips=20.0,
                tp_pips=40.0
            )
            
            self.assertIn('symbol', summary)
            self.assertIn('max_loss', summary)
            self.assertIn('max_profit', summary)
            self.assertIn('risk_reward_ratio', summary)
            
            self.assertEqual(summary['symbol'], TEST_SYMBOL)
            self.assertEqual(summary['max_loss'], 20.0)  # 20 pips * 1.0 pip_value
            self.assertEqual(summary['max_profit'], 40.0)  # 40 pips * 1.0 pip_value
            self.assertEqual(summary['risk_reward_ratio'], 2.0)  # 40/20


if __name__ == '__main__':
    unittest.main()
