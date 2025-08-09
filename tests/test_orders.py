"""
Unit tests for Order Management Module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.orders import OrderManager
from modules.logging_utils import BotLogger
from tests import MOCK_ACCOUNT_INFO, MOCK_SYMBOL_INFO, MOCK_TICK_DATA, TEST_SYMBOL, TEST_LOT_SIZE


class MockMT5:
    """Mock MT5 instance for testing."""
    
    # Order types
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    
    # Trade actions
    TRADE_ACTION_DEAL = 1
    TRADE_ACTION_SLTP = 2
    
    # Return codes
    TRADE_RETCODE_DONE = 10009
    TRADE_RETCODE_ERROR = 10013
    
    # Order time types
    ORDER_TIME_GTC = 0
    
    # Order filling types
    ORDER_FILLING_IOC = 1
    
    # Position types
    POSITION_TYPE_BUY = 0
    POSITION_TYPE_SELL = 1


class MockOrderResult:
    """Mock order result object."""
    
    def __init__(self, retcode, order=None, deal=None):
        self.retcode = retcode
        self.order = order
        self.deal = deal


class MockPosition:
    """Mock position object."""
    
    def __init__(self, ticket, symbol, volume, type_pos, price_open, magic=0):
        self.ticket = ticket
        self.symbol = symbol
        self.volume = volume
        self.type = type_pos
        self.price_open = price_open
        self.magic = magic
        self.sl = 0.0
        self.tp = 0.0
        self.profit = 0.0
        self.swap = 0.0
        self.comment = "Test position"


class MockDeal:
    """Mock deal object."""
    
    def __init__(self, ticket, order, symbol, volume, price, profit=0.0):
        self.ticket = ticket
        self.order = order
        self.symbol = symbol
        self.volume = volume
        self.price = price
        self.profit = profit
        self.time = int(time.time())
        self.type = 0
        self.entry = 0
        self.magic = 0
        self.position_id = ticket
        self.reason = 0
        self.commission = 0.0
        self.swap = 0.0
        self.comment = "Test deal"
        self.external_id = ""


class TestOrderManager(unittest.TestCase):
    """Test cases for OrderManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = Mock(spec=BotLogger)
        self.mt5 = MockMT5()
        
        # Create mocks for dependencies
        self.symbol_manager = Mock()
        self.risk_manager = Mock()
        self.account_manager = Mock()
        
        # Configure symbol manager
        self.symbol_manager.validate_and_activate_symbol.return_value = True
        self.symbol_manager.get_tick_data.return_value = MOCK_TICK_DATA
        self.symbol_manager.get_symbol_info.return_value = MOCK_SYMBOL_INFO
        
        # Configure account manager
        self.account_manager.get_position_count.return_value = 0
        
        # Configure risk manager
        self.risk_manager.parse_tp_sl_input.return_value = {
            'price_level': 1.08600,
            'pips': 10.0,
            'expected_profit': 10.0
        }
        self.risk_manager.validate_tp_sl_levels.return_value = True
        
        # Mock MT5 methods
        self.mt5.order_send = Mock()
        self.mt5.positions_get = Mock()
        self.mt5.history_deals_get = Mock()
        self.mt5.symbol_info_tick = Mock()
        
        self.order_manager = OrderManager(
            self.logger, self.mt5, self.symbol_manager, 
            self.risk_manager, self.account_manager
        )
    
    def test_open_order_success(self):
        """Test successful order opening."""
        # Mock successful order result
        self.mt5.order_send.return_value = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_DONE,
            order=123456
        )
        
        result = self.order_manager.open_order(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            action="BUY",
            sl_input="20",
            tp_input="40",
            sl_unit="pips",
            tp_unit="pips"
        )
        
        self.assertTrue(result)
        self.mt5.order_send.assert_called_once()
    
    def test_open_order_rate_limiting(self):
        """Test order rate limiting."""
        # First order should succeed
        self.mt5.order_send.return_value = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_DONE,
            order=123456
        )
        
        # First order
        result1 = self.order_manager.open_order(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            action="BUY"
        )
        
        # Immediate second order should be rate limited
        result2 = self.order_manager.open_order(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            action="BUY"
        )
        
        self.assertTrue(result1)
        self.assertFalse(result2)  # Should be rate limited
    
    def test_open_order_max_positions(self):
        """Test order rejection when max positions reached."""
        # Mock max positions reached
        self.account_manager.get_position_count.return_value = 10  # MAX_POSITIONS
        
        result = self.order_manager.open_order(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            action="BUY"
        )
        
        self.assertFalse(result)
        self.mt5.order_send.assert_not_called()
    
    def test_open_order_symbol_validation_failure(self):
        """Test order failure when symbol validation fails."""
        self.symbol_manager.validate_and_activate_symbol.return_value = False
        
        result = self.order_manager.open_order(
            symbol="INVALID",
            lot_size=TEST_LOT_SIZE,
            action="BUY"
        )
        
        self.assertFalse(result)
        self.mt5.order_send.assert_not_called()
    
    def test_open_order_no_tick_data(self):
        """Test order failure when no tick data available."""
        self.symbol_manager.get_tick_data.return_value = None
        
        result = self.order_manager.open_order(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            action="BUY"
        )
        
        self.assertFalse(result)
        self.mt5.order_send.assert_not_called()
    
    def test_open_order_invalid_action(self):
        """Test order failure with invalid action."""
        result = self.order_manager.open_order(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            action="INVALID"
        )
        
        self.assertFalse(result)
        self.mt5.order_send.assert_not_called()
    
    def test_open_order_tp_sl_validation_failure(self):
        """Test order failure when TP/SL validation fails."""
        self.risk_manager.validate_tp_sl_levels.return_value = False
        
        result = self.order_manager.open_order(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            action="BUY",
            sl_input="20",
            tp_input="40"
        )
        
        self.assertFalse(result)
        self.mt5.order_send.assert_not_called()
    
    def test_calculate_tp_sl_levels(self):
        """Test TP/SL level calculation."""
        # Mock risk manager responses
        tp_result = {'price_level': 1.08600, 'pips': 10.0}
        sl_result = {'price_level': 1.08400, 'pips': 10.0}
        
        self.risk_manager.parse_tp_sl_input.side_effect = [tp_result, sl_result]
        
        tp_price, sl_price = self.order_manager._calculate_tp_sl_levels(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            current_price=1.08500,
            action="BUY",
            tp_input="40",
            sl_input="20",
            tp_unit="pips",
            sl_unit="pips"
        )
        
        self.assertEqual(tp_price, 1.08600)
        self.assertEqual(sl_price, 1.08400)
    
    def test_calculate_tp_sl_levels_empty_input(self):
        """Test TP/SL calculation with empty inputs."""
        tp_price, sl_price = self.order_manager._calculate_tp_sl_levels(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            current_price=1.08500,
            action="BUY",
            tp_input="",
            sl_input="",
            tp_unit="pips",
            sl_unit="pips"
        )
        
        self.assertEqual(tp_price, 0.0)
        self.assertEqual(sl_price, 0.0)
    
    def test_create_order_request_buy(self):
        """Test order request creation for BUY order."""
        request = self.order_manager._create_order_request(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            order_type=self.mt5.ORDER_TYPE_BUY,
            price=1.08520,
            tp_price=1.08600,
            sl_price=1.08400
        )
        
        self.assertEqual(request['action'], self.mt5.TRADE_ACTION_DEAL)
        self.assertEqual(request['symbol'], TEST_SYMBOL)
        self.assertEqual(request['volume'], TEST_LOT_SIZE)
        self.assertEqual(request['type'], self.mt5.ORDER_TYPE_BUY)
        self.assertEqual(request['price'], 1.08520)
        self.assertEqual(request['tp'], 1.08600)
        self.assertEqual(request['sl'], 1.08400)
        self.assertEqual(request['comment'], "AutoBotCuan")
    
    def test_create_order_request_no_tp_sl(self):
        """Test order request creation without TP/SL."""
        request = self.order_manager._create_order_request(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            order_type=self.mt5.ORDER_TYPE_BUY,
            price=1.08520,
            tp_price=0.0,
            sl_price=0.0
        )
        
        self.assertNotIn('tp', request)
        self.assertNotIn('sl', request)
    
    def test_process_order_result_success(self):
        """Test processing successful order result."""
        result = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_DONE,
            order=123456
        )
        
        success = self.order_manager._process_order_result(result, TEST_SYMBOL, "BUY")
        
        self.assertTrue(success)
    
    def test_process_order_result_failure(self):
        """Test processing failed order result."""
        result = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_ERROR
        )
        
        success = self.order_manager._process_order_result(result, TEST_SYMBOL, "BUY")
        
        self.assertFalse(success)
    
    def test_process_order_result_none(self):
        """Test processing None order result."""
        success = self.order_manager._process_order_result(None, TEST_SYMBOL, "BUY")
        
        self.assertFalse(success)
    
    def test_get_retcode_description(self):
        """Test return code description mapping."""
        description = self.order_manager._get_retcode_description(self.mt5.TRADE_RETCODE_DONE)
        self.assertEqual(description, "Request completed")
        
        description = self.order_manager._get_retcode_description(10013)
        self.assertEqual(description, "Invalid request")
        
        description = self.order_manager._get_retcode_description(99999)
        self.assertTrue(description.startswith("Unknown error code"))
    
    def test_close_position_success(self):
        """Test successful position closing."""
        # Mock position
        position = MockPosition(
            ticket=123456,
            symbol=TEST_SYMBOL,
            volume=TEST_LOT_SIZE,
            type_pos=self.mt5.POSITION_TYPE_BUY,
            price_open=1.08500
        )
        
        self.mt5.positions_get.return_value = [position]
        self.mt5.symbol_info_tick.return_value = Mock(bid=1.08520, ask=1.08540)
        self.mt5.order_send.return_value = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_DONE
        )
        
        result = self.order_manager.close_position(123456)
        
        self.assertTrue(result)
        self.mt5.order_send.assert_called_once()
    
    def test_close_position_not_found(self):
        """Test closing non-existent position."""
        self.mt5.positions_get.return_value = []
        
        result = self.order_manager.close_position(999999)
        
        self.assertFalse(result)
        self.mt5.order_send.assert_not_called()
    
    def test_close_position_failure(self):
        """Test failed position closing."""
        position = MockPosition(
            ticket=123456,
            symbol=TEST_SYMBOL,
            volume=TEST_LOT_SIZE,
            type_pos=self.mt5.POSITION_TYPE_BUY,
            price_open=1.08500
        )
        
        self.mt5.positions_get.return_value = [position]
        self.mt5.symbol_info_tick.return_value = Mock(bid=1.08520, ask=1.08540)
        self.mt5.order_send.return_value = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_ERROR
        )
        
        result = self.order_manager.close_position(123456)
        
        self.assertFalse(result)
    
    def test_close_all_positions_success(self):
        """Test closing all positions successfully."""
        # Mock positions
        positions = [
            {
                'ticket': 123456,
                'symbol': TEST_SYMBOL,
                'volume': TEST_LOT_SIZE,
                'type': self.mt5.POSITION_TYPE_BUY
            },
            {
                'ticket': 123457,
                'symbol': 'GBPUSD',
                'volume': 0.02,
                'type': self.mt5.POSITION_TYPE_SELL
            }
        ]
        
        self.account_manager.get_positions.return_value = positions
        
        # Mock successful position closes
        with patch.object(self.order_manager, 'close_position', return_value=True):
            result = self.order_manager.close_all_positions()
            
        self.assertTrue(result)
    
    def test_close_all_positions_no_positions(self):
        """Test closing all positions when none exist."""
        self.account_manager.get_positions.return_value = []
        
        result = self.order_manager.close_all_positions()
        
        self.assertTrue(result)
    
    def test_close_all_positions_partial_failure(self):
        """Test closing all positions with some failures."""
        positions = [
            {'ticket': 123456},
            {'ticket': 123457}
        ]
        
        self.account_manager.get_positions.return_value = positions
        
        # Mock mixed results
        with patch.object(self.order_manager, 'close_position', side_effect=[True, False]):
            result = self.order_manager.close_all_positions()
            
        self.assertFalse(result)  # Should fail if not all positions closed
    
    def test_modify_position_success(self):
        """Test successful position modification."""
        position = MockPosition(
            ticket=123456,
            symbol=TEST_SYMBOL,
            volume=TEST_LOT_SIZE,
            type_pos=self.mt5.POSITION_TYPE_BUY,
            price_open=1.08500
        )
        
        self.mt5.positions_get.return_value = [position]
        self.mt5.order_send.return_value = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_DONE
        )
        
        result = self.order_manager.modify_position(
            ticket=123456,
            new_sl=1.08400,
            new_tp=1.08600
        )
        
        self.assertTrue(result)
        
        # Check that correct request was sent
        call_args = self.mt5.order_send.call_args[0][0]
        self.assertEqual(call_args['action'], self.mt5.TRADE_ACTION_SLTP)
        self.assertEqual(call_args['position'], 123456)
        self.assertEqual(call_args['sl'], 1.08400)
        self.assertEqual(call_args['tp'], 1.08600)
    
    def test_modify_position_not_found(self):
        """Test modifying non-existent position."""
        self.mt5.positions_get.return_value = []
        
        result = self.order_manager.modify_position(
            ticket=999999,
            new_sl=1.08400
        )
        
        self.assertFalse(result)
        self.mt5.order_send.assert_not_called()
    
    def test_modify_position_failure(self):
        """Test failed position modification."""
        position = MockPosition(
            ticket=123456,
            symbol=TEST_SYMBOL,
            volume=TEST_LOT_SIZE,
            type_pos=self.mt5.POSITION_TYPE_BUY,
            price_open=1.08500
        )
        
        self.mt5.positions_get.return_value = [position]
        self.mt5.order_send.return_value = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_ERROR
        )
        
        result = self.order_manager.modify_position(
            ticket=123456,
            new_sl=1.08400
        )
        
        self.assertFalse(result)
    
    def test_get_order_history(self):
        """Test getting order history."""
        # Mock deals
        deals = [
            MockDeal(
                ticket=123456,
                order=789012,
                symbol=TEST_SYMBOL,
                volume=TEST_LOT_SIZE,
                price=1.08520,
                profit=10.0
            ),
            MockDeal(
                ticket=123457,
                order=789013,
                symbol='GBPUSD',
                volume=0.02,
                price=1.25400,
                profit=-5.0
            )
        ]
        
        self.mt5.history_deals_get.return_value = deals
        
        history = self.order_manager.get_order_history(days=7)
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['ticket'], 123456)
        self.assertEqual(history[0]['symbol'], TEST_SYMBOL)
        self.assertEqual(history[0]['profit'], 10.0)
        self.assertEqual(history[1]['ticket'], 123457)
        self.assertEqual(history[1]['symbol'], 'GBPUSD')
        self.assertEqual(history[1]['profit'], -5.0)
    
    def test_get_order_history_no_deals(self):
        """Test getting order history with no deals."""
        self.mt5.history_deals_get.return_value = None
        
        history = self.order_manager.get_order_history(days=7)
        
        self.assertEqual(history, [])
    
    def test_get_order_history_empty_deals(self):
        """Test getting order history with empty deals."""
        self.mt5.history_deals_get.return_value = []
        
        history = self.order_manager.get_order_history(days=7)
        
        self.assertEqual(history, [])
    
    def test_open_order_buy_type_and_price(self):
        """Test that BUY orders use correct type and ask price."""
        self.mt5.order_send.return_value = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_DONE,
            order=123456
        )
        
        result = self.order_manager.open_order(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            action="BUY"
        )
        
        # Check that order was sent with correct parameters
        call_args = self.mt5.order_send.call_args[0][0]
        self.assertEqual(call_args['type'], self.mt5.ORDER_TYPE_BUY)
        self.assertEqual(call_args['price'], MOCK_TICK_DATA['ask'])
    
    def test_open_order_sell_type_and_price(self):
        """Test that SELL orders use correct type and bid price."""
        self.mt5.order_send.return_value = MockOrderResult(
            retcode=self.mt5.TRADE_RETCODE_DONE,
            order=123456
        )
        
        result = self.order_manager.open_order(
            symbol=TEST_SYMBOL,
            lot_size=TEST_LOT_SIZE,
            action="SELL"
        )
        
        # Check that order was sent with correct parameters
        call_args = self.mt5.order_send.call_args[0][0]
        self.assertEqual(call_args['type'], self.mt5.ORDER_TYPE_SELL)
        self.assertEqual(call_args['price'], MOCK_TICK_DATA['bid'])
    
    def test_order_manager_thread_safety(self):
        """Test thread safety of order manager."""
        import threading
        import time
        
        results = []
        
        def place_order():
            self.mt5.order_send.return_value = MockOrderResult(
                retcode=self.mt5.TRADE_RETCODE_DONE,
                order=123456
            )
            
            # Reset rate limiting for each thread
            time.sleep(0.1)
            result = self.order_manager.open_order(
                symbol=f"{TEST_SYMBOL}_{threading.current_thread().ident}",
                lot_size=TEST_LOT_SIZE,
                action="BUY"
            )
            results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=place_order)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All orders should succeed (different symbols, no rate limiting)
        self.assertEqual(len(results), 3)


if __name__ == '__main__':
    unittest.main()
