"""
Order Management Module
Handles order execution, modification, and position management.
"""

import time
from typing import Optional, Dict, Any, List
import threading

from config import *


class OrderManager:
    """Manages order execution and position operations."""
    
    def __init__(self, logger, mt5_instance, symbol_manager, risk_manager, account_manager):
        """Initialize order manager."""
        self.logger = logger
        self.mt5 = mt5_instance
        self.symbol_manager = symbol_manager
        self.risk_manager = risk_manager
        self.account_manager = account_manager
        
        self.order_lock = threading.Lock()
        self.last_order_time = {}
        self.rate_limit_window = 3  # seconds
        
    def open_order(self, symbol: str, lot_size: float, action: str, 
                   sl_input: str = "", tp_input: str = "", 
                   sl_unit: str = 'pips', tp_unit: str = 'pips') -> bool:
        """
        Open a new trading order with comprehensive validation.
        
        Args:
            symbol: Trading symbol
            lot_size: Lot size
            action: 'BUY' or 'SELL'
            sl_input: Stop loss input value
            tp_input: Take profit input value
            sl_unit: Stop loss unit type
            tp_unit: Take profit unit type
            
        Returns:
            bool: True if order executed successfully
        """
        with self.order_lock:
            try:
                # Rate limiting
                current_time = time.time()
                last_trade_time = self.last_order_time.get(symbol, 0)
                if current_time - last_trade_time < self.rate_limit_window:
                    self.logger.log(f"⚠️ Rate limit: Too soon to trade {symbol}")
                    return False
                
                # Validate position count
                position_count = self.account_manager.get_position_count()
                if position_count >= MAX_POSITIONS:
                    self.logger.log(f"⚠️ Maximum positions reached: {position_count}")
                    return False
                
                # Validate and activate symbol
                if not self.symbol_manager.validate_and_activate_symbol(symbol):
                    self.logger.log(f"❌ Failed to validate symbol: {symbol}")
                    return False
                
                # Get current tick data
                tick_data = self.symbol_manager.get_tick_data(symbol, retries=3)
                if not tick_data:
                    self.logger.log(f"❌ Cannot get tick data for {symbol}")
                    return False
                
                # Determine order type and price
                action_upper = action.upper()
                if action_upper == "BUY":
                    order_type = self.mt5.ORDER_TYPE_BUY
                    current_price = tick_data['ask']
                elif action_upper == "SELL":
                    order_type = self.mt5.ORDER_TYPE_SELL
                    current_price = tick_data['bid']
                else:
                    self.logger.log(f"❌ Invalid action: {action}")
                    return False
                
                # Calculate TP/SL levels
                tp_price, sl_price = self._calculate_tp_sl_levels(
                    symbol, lot_size, current_price, action_upper, 
                    tp_input, sl_input, tp_unit, sl_unit
                )
                
                # Validate TP/SL levels
                if tp_price > 0 or sl_price > 0:
                    if not self.risk_manager.validate_tp_sl_levels(
                        symbol, tp_price, sl_price, action_upper, current_price):
                        self.logger.log(f"❌ Invalid TP/SL levels for {symbol}")
                        return False
                
                # Create order request
                request = self._create_order_request(
                    symbol, lot_size, order_type, current_price, tp_price, sl_price
                )
                
                # Send order
                result = self.mt5.order_send(request)
                
                if self._process_order_result(result, symbol, action):
                    self.last_order_time[symbol] = current_time
                    return True
                else:
                    return False
                    
            except Exception as e:
                self.logger.log(f"❌ Error opening order for {symbol}: {str(e)}")
                return False
    
    def _calculate_tp_sl_levels(self, symbol: str, lot_size: float, current_price: float, 
                               action: str, tp_input: str, sl_input: str, 
                               tp_unit: str, sl_unit: str) -> tuple:
        """Calculate TP and SL price levels."""
        try:
            tp_price = 0.0
            sl_price = 0.0
            
            # Calculate TP level
            if tp_input and tp_input.strip():
                tp_result = self.risk_manager.parse_tp_sl_input(
                    tp_input, tp_unit, symbol, lot_size, current_price, action, True
                )
                if tp_result:
                    tp_price = tp_result['price_level']
            
            # Calculate SL level
            if sl_input and sl_input.strip():
                sl_result = self.risk_manager.parse_tp_sl_input(
                    sl_input, sl_unit, symbol, lot_size, current_price, action, False
                )
                if sl_result:
                    sl_price = sl_result['price_level']
            
            # Round to symbol digits
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if symbol_info:
                digits = symbol_info['digits']
                if tp_price > 0:
                    tp_price = round(tp_price, digits)
                if sl_price > 0:
                    sl_price = round(sl_price, digits)
            
            return tp_price, sl_price
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating TP/SL levels: {str(e)}")
            return 0.0, 0.0
    
    def _create_order_request(self, symbol: str, lot_size: float, order_type: int, 
                             price: float, tp_price: float, sl_price: float) -> Dict[str, Any]:
        """Create MT5 order request dictionary."""
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "deviation": DEFAULT_DEVIATION,
            "magic": DEFAULT_MAGIC_NUMBER,
            "comment": "AutoBotCuan",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }
        
        # Add TP/SL if specified
        if tp_price > 0:
            request["tp"] = tp_price
        if sl_price > 0:
            request["sl"] = sl_price
        
        return request
    
    def _process_order_result(self, result, symbol: str, action: str) -> bool:
        """Process order execution result."""
        try:
            if result is None:
                self.logger.log(f"❌ Order failed for {symbol}: No result")
                return False
            
            if hasattr(result, 'retcode'):
                retcode = result.retcode
                
                if retcode == self.mt5.TRADE_RETCODE_DONE:
                    self.logger.log(f"✅ {action} order executed for {symbol}")
                    if hasattr(result, 'order'):
                        self.logger.log(f"📋 Order ticket: {result.order}")
                    return True
                else:
                    error_msg = self._get_retcode_description(retcode)
                    self.logger.log(f"❌ Order failed for {symbol}: {error_msg} (Code: {retcode})")
                    return False
            else:
                self.logger.log(f"❌ Invalid order result for {symbol}")
                return False
                
        except Exception as e:
            self.logger.log(f"❌ Error processing order result: {str(e)}")
            return False
    
    def _get_retcode_description(self, retcode: int) -> str:
        """Get human-readable description for MT5 return codes."""
        retcode_descriptions = {
            10004: "Requote",
            10006: "Request rejected",
            10007: "Request canceled by trader", 
            10008: "Order placed",
            10009: "Request completed",
            10010: "Only part of the request was completed",
            10011: "Request processing error",
            10012: "Request canceled by timeout",
            10013: "Invalid request",
            10014: "Invalid volume in the request",
            10015: "Invalid price in the request",
            10016: "Invalid stops in the request",
            10017: "Trade is disabled",
            10018: "Market is closed",
            10019: "There is not enough money to complete the request",
            10020: "Prices changed",
            10021: "There are no quotes to process the request",
            10022: "Invalid order expiration date in the request",
            10023: "Order state changed",
            10024: "Too frequent requests",
            10025: "No changes in request",
            10026: "Autotrading disabled by server",
            10027: "Autotrading disabled by client terminal",
            10028: "Request locked for processing",
            10029: "Order or position frozen",
            10030: "Invalid order filling type",
            10031: "No connection with the trade server"
        }
        
        return retcode_descriptions.get(retcode, f"Unknown error code: {retcode}")
    
    def close_position(self, ticket: int) -> bool:
        """
        Close specific position by ticket.
        
        Args:
            ticket: Position ticket number
            
        Returns:
            bool: True if position closed successfully
        """
        try:
            # Get position info
            positions = self.mt5.positions_get(ticket=ticket)
            if not positions:
                self.logger.log(f"❌ Position not found: {ticket}")
                return False
            
            position = positions[0]
            
            # Determine close order type
            if position.type == self.mt5.POSITION_TYPE_BUY:
                order_type = self.mt5.ORDER_TYPE_SELL
                price = self.mt5.symbol_info_tick(position.symbol).bid
            else:
                order_type = self.mt5.ORDER_TYPE_BUY
                price = self.mt5.symbol_info_tick(position.symbol).ask
            
            # Create close request
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": DEFAULT_DEVIATION,
                "magic": position.magic,
                "comment": "Close position",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }
            
            # Send close request
            result = self.mt5.order_send(request)
            
            if result and result.retcode == self.mt5.TRADE_RETCODE_DONE:
                self.logger.log(f"✅ Position {ticket} closed successfully")
                return True
            else:
                retcode = result.retcode if result else "No result"
                self.logger.log(f"❌ Failed to close position {ticket}: {retcode}")
                return False
                
        except Exception as e:
            self.logger.log(f"❌ Error closing position {ticket}: {str(e)}")
            return False
    
    def close_all_positions(self) -> bool:
        """
        Close all open positions.
        
        Returns:
            bool: True if all positions closed successfully
        """
        try:
            positions = self.account_manager.get_positions()
            if not positions:
                self.logger.log("ℹ️ No positions to close")
                return True
            
            success_count = 0
            total_positions = len(positions)
            
            for position in positions:
                if self.close_position(position['ticket']):
                    success_count += 1
                time.sleep(0.1)  # Brief pause between closes
            
            self.logger.log(f"📊 Closed {success_count}/{total_positions} positions")
            return success_count == total_positions
            
        except Exception as e:
            self.logger.log(f"❌ Error closing all positions: {str(e)}")
            return False
    
    def modify_position(self, ticket: int, new_sl: float = 0, new_tp: float = 0) -> bool:
        """
        Modify position stop loss and/or take profit.
        
        Args:
            ticket: Position ticket number
            new_sl: New stop loss price (0 to remove)
            new_tp: New take profit price (0 to remove)
            
        Returns:
            bool: True if modification successful
        """
        try:
            # Get position info
            positions = self.mt5.positions_get(ticket=ticket)
            if not positions:
                self.logger.log(f"❌ Position not found: {ticket}")
                return False
            
            position = positions[0]
            
            # Create modification request
            request = {
                "action": self.mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": ticket,
                "sl": new_sl,
                "tp": new_tp
            }
            
            # Send modification request
            result = self.mt5.order_send(request)
            
            if result and result.retcode == self.mt5.TRADE_RETCODE_DONE:
                self.logger.log(f"✅ Position {ticket} modified successfully")
                return True
            else:
                retcode = result.retcode if result else "No result"
                self.logger.log(f"❌ Failed to modify position {ticket}: {retcode}")
                return False
                
        except Exception as e:
            self.logger.log(f"❌ Error modifying position {ticket}: {str(e)}")
            return False
    
    def get_order_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get order history for specified number of days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of order dictionaries
        """
        try:
            import datetime
            
            # Calculate date range
            to_date = datetime.datetime.now()
            from_date = to_date - datetime.timedelta(days=days)
            
            # Get deals (executed orders)
            deals = self.mt5.history_deals_get(from_date, to_date)
            if not deals:
                return []
            
            deal_list = []
            for deal in deals:
                deal_dict = {
                    "ticket": deal.ticket,
                    "order": deal.order,
                    "time": deal.time,
                    "type": deal.type,
                    "entry": deal.entry,
                    "magic": deal.magic,
                    "position_id": deal.position_id,
                    "reason": deal.reason,
                    "volume": deal.volume,
                    "price": deal.price,
                    "commission": deal.commission,
                    "swap": deal.swap,
                    "profit": deal.profit,
                    "symbol": deal.symbol,
                    "comment": deal.comment,
                    "external_id": deal.external_id
                }
                deal_list.append(deal_dict)
            
            return deal_list
            
        except Exception as e:
            self.logger.log(f"❌ Error getting order history: {str(e)}")
            return []
