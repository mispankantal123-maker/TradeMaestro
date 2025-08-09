"""
Risk Management Module
Handles lot sizing, TP/SL calculations, and risk controls.
"""

import math
from typing import Optional, Dict, Any, Tuple, Union
from config import *


class RiskManager:
    """Manages risk calculations and position sizing."""
    
    def __init__(self, logger, symbol_manager, account_manager):
        """Initialize risk manager."""
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.account_manager = account_manager
        
    def calculate_pip_value(self, symbol: str, lot_size: float) -> float:
        """
        Calculate pip value for a symbol and lot size.
        
        Args:
            symbol: Trading symbol
            lot_size: Lot size
            
        Returns:
            float: Pip value in account currency
        """
        try:
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if not symbol_info:
                self.logger.log(f"❌ Cannot get symbol info for {symbol}")
                return 0.0
            
            # Use tick value if available
            if symbol_info.get('trade_tick_value') and symbol_info.get('trade_tick_size'):
                tick_value = symbol_info['trade_tick_value']
                tick_size = symbol_info['trade_tick_size']
                point = symbol_info['point']
                
                if tick_size > 0 and point > 0:
                    pip_value = (tick_value / tick_size) * point * lot_size
                    return pip_value
            
            # Fallback calculation for forex pairs
            if len(symbol) >= 6:
                base_currency = symbol[:3]
                quote_currency = symbol[3:6]
                account_currency = self.account_manager.account_info.get('currency', 'USD')
                
                # Standard lot size is 100,000
                contract_size = 100000 * lot_size
                
                if quote_currency == account_currency:
                    # Direct calculation
                    pip_value = contract_size * symbol_info['point']
                else:
                    # Need conversion
                    conversion_rate = self.account_manager.get_currency_conversion_rate(
                        quote_currency, account_currency)
                    pip_value = contract_size * symbol_info['point'] * conversion_rate
                
                return pip_value
            
            # Generic fallback
            return lot_size * symbol_info['point'] * 100000
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating pip value for {symbol}: {str(e)}")
            return 10.0  # Conservative fallback
    
    def calculate_auto_lot_size(self, symbol: str, sl_pips: float, risk_percent: float = 1.0) -> float:
        """
        Calculate optimal lot size based on risk percentage and stop loss.
        
        Args:
            symbol: Trading symbol
            sl_pips: Stop loss in pips
            risk_percent: Risk percentage of account balance
            
        Returns:
            float: Calculated lot size
        """
        try:
            if sl_pips <= 0:
                self.logger.log("❌ Invalid stop loss pips for lot calculation")
                return MIN_LOT_SIZE
            
            # Get account balance
            balance = self.account_manager.get_balance()
            if balance <= 0:
                self.logger.log("❌ Invalid account balance for lot calculation")
                return MIN_LOT_SIZE
            
            # Calculate risk amount
            risk_amount = balance * (risk_percent / 100)
            
            # Get symbol info for lot constraints
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if not symbol_info:
                self.logger.log(f"❌ Cannot get symbol info for lot calculation: {symbol}")
                return MIN_LOT_SIZE
            
            # Calculate pip value per standard lot
            pip_value_per_lot = self.calculate_pip_value(symbol, 1.0)
            if pip_value_per_lot <= 0:
                self.logger.log("❌ Invalid pip value for lot calculation")
                return MIN_LOT_SIZE
            
            # Calculate lot size
            calculated_lot = risk_amount / (sl_pips * pip_value_per_lot)
            
            # Apply symbol constraints
            volume_min = symbol_info.get('volume_min', MIN_LOT_SIZE)
            volume_max = symbol_info.get('volume_max', MAX_LOT_SIZE)
            volume_step = symbol_info.get('volume_step', 0.01)
            
            # Round to step
            calculated_lot = math.floor(calculated_lot / volume_step) * volume_step
            
            # Apply limits
            calculated_lot = max(volume_min, min(volume_max, calculated_lot))
            
            self.logger.log(f"💰 Auto lot calculation: {calculated_lot} lots for {risk_percent}% risk")
            return calculated_lot
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating auto lot size: {str(e)}")
            return MIN_LOT_SIZE
    
    def parse_tp_sl_input(self, input_value: str, unit: str, symbol: str, 
                         lot_size: float, current_price: float, 
                         order_type: str, is_tp: bool = True) -> Optional[Dict[str, Any]]:
        """
        Parse TP/SL input with multiple unit support.
        
        Args:
            input_value: Input value as string
            unit: Unit type ('pips', 'price', '%', currency name)
            symbol: Trading symbol
            lot_size: Lot size
            current_price: Current market price
            order_type: 'BUY' or 'SELL'
            is_tp: True for TP, False for SL
            
        Returns:
            Dict with parsed TP/SL information or None
        """
        try:
            if not input_value or input_value.strip() == "":
                return None
            
            value = float(input_value.strip())
            if value <= 0:
                return None
            
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if not symbol_info:
                return None
            
            result = {
                "original_value": value,
                "unit": unit,
                "price_level": 0.0,
                "pips": 0.0,
                "expected_profit": 0.0,
                "risk_reward_ratio": 0.0
            }
            
            if unit.lower() == "pips":
                # Pips input
                result["pips"] = value
                pip_distance = value * symbol_info['point']
                
                if order_type.upper() == "BUY":
                    if is_tp:
                        result["price_level"] = current_price + pip_distance
                    else:
                        result["price_level"] = current_price - pip_distance
                else:  # SELL
                    if is_tp:
                        result["price_level"] = current_price - pip_distance
                    else:
                        result["price_level"] = current_price + pip_distance
                        
            elif unit.lower() == "price":
                # Price level input
                result["price_level"] = value
                pip_distance = abs(value - current_price) / symbol_info['point']
                result["pips"] = pip_distance
                
            elif unit.lower() == "%":
                # Percentage input
                balance = self.account_manager.get_balance()
                target_amount = balance * (value / 100)
                
                pip_value = self.calculate_pip_value(symbol, lot_size)
                if pip_value > 0:
                    required_pips = target_amount / pip_value
                    result["pips"] = required_pips
                    
                    pip_distance = required_pips * symbol_info['point']
                    if order_type.upper() == "BUY":
                        if is_tp:
                            result["price_level"] = current_price + pip_distance
                        else:
                            result["price_level"] = current_price - pip_distance
                    else:  # SELL
                        if is_tp:
                            result["price_level"] = current_price - pip_distance
                        else:
                            result["price_level"] = current_price + pip_distance
                            
            else:
                # Currency amount input
                target_currency = unit.upper()
                account_currency = self.account_manager.account_info.get('currency', 'USD')
                
                # Convert to account currency if needed
                if target_currency == "CURRENCY":
                    target_amount = value
                else:
                    conversion_rate = self.account_manager.get_currency_conversion_rate(
                        target_currency, account_currency)
                    target_amount = value * conversion_rate
                
                pip_value = self.calculate_pip_value(symbol, lot_size)
                if pip_value > 0:
                    required_pips = target_amount / pip_value
                    result["pips"] = required_pips
                    
                    pip_distance = required_pips * symbol_info['point']
                    if order_type.upper() == "BUY":
                        if is_tp:
                            result["price_level"] = current_price + pip_distance
                        else:
                            result["price_level"] = current_price - pip_distance
                    else:  # SELL
                        if is_tp:
                            result["price_level"] = current_price - pip_distance
                        else:
                            result["price_level"] = current_price + pip_distance
            
            # Calculate expected profit/loss
            pip_value = self.calculate_pip_value(symbol, lot_size)
            result["expected_profit"] = result["pips"] * pip_value * (1 if is_tp else -1)
            
            return result
            
        except Exception as e:
            self.logger.log(f"❌ Error parsing TP/SL input: {str(e)}")
            return None
    
    def validate_tp_sl_levels(self, symbol: str, tp_price: float, sl_price: float, 
                             order_type: str, current_price: float) -> bool:
        """
        Validate TP/SL levels against broker requirements.
        
        Args:
            symbol: Trading symbol
            tp_price: Take profit price
            sl_price: Stop loss price
            order_type: 'BUY' or 'SELL'
            current_price: Current market price
            
        Returns:
            bool: True if levels are valid
        """
        try:
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if not symbol_info:
                return False
            
            # Get minimum stop level
            stop_level = getattr(symbol_info, 'trade_stops_level', 0) * symbol_info['point']
            if stop_level == 0:
                stop_level = 5 * symbol_info['point']  # Fallback minimum
            
            # Add safety margin
            safety_margin = 2 * symbol_info['point']
            min_distance = stop_level + safety_margin
            
            if order_type.upper() == "BUY":
                # BUY order validation
                if tp_price > 0:
                    if tp_price <= current_price:
                        self.logger.log("❌ TP must be above current price for BUY")
                        return False
                    if (tp_price - current_price) < min_distance:
                        self.logger.log(f"❌ TP too close to current price. Min distance: {min_distance}")
                        return False
                
                if sl_price > 0:
                    if sl_price >= current_price:
                        self.logger.log("❌ SL must be below current price for BUY")
                        return False
                    if (current_price - sl_price) < min_distance:
                        self.logger.log(f"❌ SL too close to current price. Min distance: {min_distance}")
                        return False
                        
            else:  # SELL order
                if tp_price > 0:
                    if tp_price >= current_price:
                        self.logger.log("❌ TP must be below current price for SELL")
                        return False
                    if (current_price - tp_price) < min_distance:
                        self.logger.log(f"❌ TP too close to current price. Min distance: {min_distance}")
                        return False
                
                if sl_price > 0:
                    if sl_price <= current_price:
                        self.logger.log("❌ SL must be above current price for SELL")
                        return False
                    if (sl_price - current_price) < min_distance:
                        self.logger.log(f"❌ SL too close to current price. Min distance: {min_distance}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error validating TP/SL levels: {str(e)}")
            return False
    
    def calculate_risk_reward_ratio(self, tp_pips: float, sl_pips: float) -> float:
        """
        Calculate risk-reward ratio.
        
        Args:
            tp_pips: Take profit in pips
            sl_pips: Stop loss in pips
            
        Returns:
            float: Risk-reward ratio
        """
        try:
            if sl_pips <= 0:
                return 0.0
            return tp_pips / sl_pips
        except:
            return 0.0
    
    def validate_position_size(self, symbol: str, lot_size: float) -> bool:
        """
        Validate if position size is acceptable based on account constraints.
        
        Args:
            symbol: Trading symbol
            lot_size: Proposed lot size
            
        Returns:
            bool: True if position size is acceptable
        """
        try:
            # Check symbol constraints
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if not symbol_info:
                return False
            
            volume_min = symbol_info.get('volume_min', MIN_LOT_SIZE)
            volume_max = symbol_info.get('volume_max', MAX_LOT_SIZE)
            
            if lot_size < volume_min or lot_size > volume_max:
                self.logger.log(f"❌ Lot size {lot_size} outside allowed range [{volume_min}, {volume_max}]")
                return False
            
            # Check margin requirement
            margin_required = self.account_manager.calculate_margin_requirement(
                symbol, lot_size, 0)  # Order type doesn't matter for margin calc
            
            free_margin = self.account_manager.get_free_margin()
            
            if margin_required > free_margin * 0.8:  # Use 80% of available margin
                self.logger.log(f"❌ Insufficient margin. Required: {margin_required}, Available: {free_margin}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error validating position size: {str(e)}")
            return False
    
    def get_risk_summary(self, symbol: str, lot_size: float, sl_pips: float, tp_pips: float) -> Dict[str, Any]:
        """
        Get comprehensive risk summary for a potential trade.
        
        Args:
            symbol: Trading symbol
            lot_size: Lot size
            sl_pips: Stop loss in pips
            tp_pips: Take profit in pips
            
        Returns:
            Dict with risk analysis
        """
        try:
            pip_value = self.calculate_pip_value(symbol, lot_size)
            balance = self.account_manager.get_balance()
            
            max_loss = sl_pips * pip_value
            max_profit = tp_pips * pip_value
            risk_percent = (max_loss / balance) * 100 if balance > 0 else 0
            reward_percent = (max_profit / balance) * 100 if balance > 0 else 0
            risk_reward_ratio = self.calculate_risk_reward_ratio(tp_pips, sl_pips)
            
            return {
                "symbol": symbol,
                "lot_size": lot_size,
                "pip_value": pip_value,
                "sl_pips": sl_pips,
                "tp_pips": tp_pips,
                "max_loss": max_loss,
                "max_profit": max_profit,
                "risk_percent": risk_percent,
                "reward_percent": reward_percent,
                "risk_reward_ratio": risk_reward_ratio,
                "account_balance": balance
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating risk summary: {str(e)}")
            return {}
