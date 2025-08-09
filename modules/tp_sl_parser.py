"""
TP/SL Multi-Unit Parser Module
Implements comprehensive TP/SL parsing system from bobot2.py lines 1200-1350
Supports pips, price, %, and currency units (USD, EUR, GBP, CAD, AUD, JPY, CHF, NZD)
"""

import re
from typing import Optional, Dict, Any, Tuple, Union
from config import *


class TPSLParser:
    """Advanced TP/SL parser supporting multiple units from bobot2.py."""
    
    def __init__(self, logger, symbol_manager, account_manager):
        """Initialize TP/SL parser."""
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.account_manager = account_manager
        
        # Supported currency codes
        self.supported_currencies = {
            'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'NZD'
        }
        
        # Unit patterns for parsing
        self.unit_patterns = {
            'pips': r'^(\d+(?:\.\d+)?)\s*(?:pips?|p)$',
            'price': r'^(\d+(?:\.\d+)?)$',
            'percent': r'^(\d+(?:\.\d+)?)\s*%$',
            'currency': r'^(\d+(?:\.\d+)?)\s*([A-Z]{3})$'
        }
    
    def parse_tp_sl_input(self, input_value: str, unit: str, symbol: str, 
                         current_price: float, action: str) -> Optional[float]:
        """
        Parse TP/SL input with multi-unit support from bobot2.py.
        
        Args:
            input_value: Input string (e.g., "20", "1.2050", "2%", "100USD")
            unit: Unit type ("pips", "price", "%", "currency")
            symbol: Trading symbol
            current_price: Current market price
            action: Trade action ("BUY" or "SELL")
            
        Returns:
            float: Calculated TP/SL price or None if invalid
        """
        try:
            if not input_value or not input_value.strip():
                return None
            
            input_clean = input_value.strip().upper()
            
            # Get symbol info
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if not symbol_info:
                self.logger.log(f"❌ Cannot get symbol info for TP/SL calculation: {symbol}")
                return None
            
            point = symbol_info.get('point', 0.0001)
            digits = symbol_info.get('digits', 5)
            
            # Parse based on unit type
            if unit.lower() == "pips":
                return self._parse_pips(input_clean, symbol, current_price, action, point)
            elif unit.lower() == "price":
                return self._parse_price(input_clean, current_price, action, digits)
            elif unit.lower() == "%":
                return self._parse_percent(input_clean, current_price, action)
            elif unit.lower() == "currency":
                return self._parse_currency(input_clean, symbol, current_price, action)
            else:
                self.logger.log(f"❌ Unsupported TP/SL unit: {unit}")
                return None
                
        except Exception as e:
            self.logger.log(f"❌ Error parsing TP/SL input '{input_value}': {str(e)}")
            return None
    
    def _parse_pips(self, input_value: str, symbol: str, current_price: float, 
                   action: str, point: float) -> Optional[float]:
        """Parse pips input."""
        try:
            # Extract numeric value
            match = re.match(self.unit_patterns['pips'], input_value)
            if not match:
                # Try direct numeric input
                try:
                    pips = float(input_value)
                except ValueError:
                    self.logger.log(f"❌ Invalid pips format: {input_value}")
                    return None
            else:
                pips = float(match.group(1))
            
            if pips <= 0:
                self.logger.log(f"❌ Invalid pips value: {pips}")
                return None
            
            # Calculate price based on action
            pip_value = pips * point
            
            if action.upper() == "BUY":
                # For TP: add pips, for SL: subtract pips
                return current_price + pip_value
            else:  # SELL
                # For TP: subtract pips, for SL: add pips  
                return current_price - pip_value
                
        except Exception as e:
            self.logger.log(f"❌ Error parsing pips: {str(e)}")
            return None
    
    def _parse_price(self, input_value: str, current_price: float, 
                    action: str, digits: int) -> Optional[float]:
        """Parse direct price input."""
        try:
            # Extract numeric value
            match = re.match(self.unit_patterns['price'], input_value)
            if not match:
                try:
                    price = float(input_value)
                except ValueError:
                    self.logger.log(f"❌ Invalid price format: {input_value}")
                    return None
            else:
                price = float(match.group(1))
            
            if price <= 0:
                self.logger.log(f"❌ Invalid price value: {price}")
                return None
            
            # Round to symbol digits
            price = round(price, digits)
            
            # Validate price direction
            if action.upper() == "BUY":
                # For BUY: TP should be above current, SL below
                if abs(price - current_price) < (current_price * 0.0001):  # Too close
                    self.logger.log(f"⚠️ Price too close to current: {price} vs {current_price}")
                    return None
            else:  # SELL
                # For SELL: TP should be below current, SL above
                if abs(price - current_price) < (current_price * 0.0001):
                    self.logger.log(f"⚠️ Price too close to current: {price} vs {current_price}")
                    return None
            
            return price
            
        except Exception as e:
            self.logger.log(f"❌ Error parsing price: {str(e)}")
            return None
    
    def _parse_percent(self, input_value: str, current_price: float, action: str) -> Optional[float]:
        """Parse percentage input."""
        try:
            # Extract numeric value
            match = re.match(self.unit_patterns['percent'], input_value)
            if not match:
                self.logger.log(f"❌ Invalid percent format: {input_value}")
                return None
            
            percent = float(match.group(1))
            
            if percent <= 0 or percent > 50:  # Reasonable limits
                self.logger.log(f"❌ Invalid percent value: {percent}%")
                return None
            
            # Calculate price based on percentage
            percent_value = current_price * (percent / 100)
            
            if action.upper() == "BUY":
                # For TP: add percentage, for SL: subtract percentage
                return current_price + percent_value
            else:  # SELL
                # For TP: subtract percentage, for SL: add percentage
                return current_price - percent_value
                
        except Exception as e:
            self.logger.log(f"❌ Error parsing percent: {str(e)}")
            return None
    
    def _parse_currency(self, input_value: str, symbol: str, current_price: float, 
                       action: str) -> Optional[float]:
        """Parse currency amount input."""
        try:
            # Extract numeric value and currency
            match = re.match(self.unit_patterns['currency'], input_value)
            if not match:
                self.logger.log(f"❌ Invalid currency format: {input_value}")
                return None
            
            amount = float(match.group(1))
            currency = match.group(2)
            
            if amount <= 0:
                self.logger.log(f"❌ Invalid currency amount: {amount}")
                return None
            
            if currency not in self.supported_currencies:
                self.logger.log(f"❌ Unsupported currency: {currency}")
                return None
            
            # Get account currency
            account_currency = self.account_manager.account_info.get('currency', 'USD')
            
            # Convert amount to account currency if needed
            if currency != account_currency:
                conversion_rate = self.account_manager.get_currency_conversion_rate(
                    currency, account_currency)
                if conversion_rate <= 0:
                    self.logger.log(f"❌ Cannot get conversion rate for {currency}")
                    return None
                amount *= conversion_rate
            
            # Calculate pip value for the symbol
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            point = symbol_info.get('point', 0.0001)
            
            # Estimate pip value (simplified)
            pip_value = self._calculate_pip_value_for_currency(symbol, 1.0)
            if pip_value <= 0:
                self.logger.log(f"❌ Cannot calculate pip value for {symbol}")
                return None
            
            # Calculate required pips
            required_pips = amount / pip_value
            pip_price_change = required_pips * point
            
            if action.upper() == "BUY":
                return current_price + pip_price_change
            else:  # SELL
                return current_price - pip_price_change
                
        except Exception as e:
            self.logger.log(f"❌ Error parsing currency: {str(e)}")
            return None
    
    def _calculate_pip_value_for_currency(self, symbol: str, lot_size: float) -> float:
        """Calculate pip value for currency calculation."""
        try:
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if not symbol_info:
                return 10.0  # Default fallback
            
            # Use tick value if available
            if symbol_info.get('trade_tick_value') and symbol_info.get('trade_tick_size'):
                tick_value = symbol_info['trade_tick_value']
                tick_size = symbol_info['trade_tick_size']
                point = symbol_info['point']
                
                if tick_size > 0 and point > 0:
                    return (tick_value / tick_size) * point * lot_size
            
            # Fallback calculation
            return lot_size * symbol_info.get('point', 0.0001) * 100000
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating pip value: {str(e)}")
            return 10.0
    
    def validate_tp_sl_levels(self, symbol: str, current_price: float, tp_price: Optional[float], 
                             sl_price: Optional[float], action: str) -> Tuple[bool, str]:
        """
        Validate TP/SL levels against symbol constraints from bobot2.py.
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            tp_price: Take profit price (optional)
            sl_price: Stop loss price (optional)
            action: Trade action ("BUY" or "SELL")
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if not symbol_info:
                return False, f"Cannot get symbol info for {symbol}"
            
            # Get symbol constraints
            stops_level = symbol_info.get('trade_stops_level', 10)
            point = symbol_info.get('point', 0.0001)
            spread = symbol_info.get('spread', 20)
            
            # Minimum distance in price
            min_distance = max(stops_level * point, spread * point * 2)
            
            action_upper = action.upper()
            
            # Validate TP
            if tp_price is not None:
                if action_upper == "BUY":
                    if tp_price <= current_price:
                        return False, f"TP for BUY must be above current price: {tp_price} <= {current_price}"
                    if (tp_price - current_price) < min_distance:
                        return False, f"TP too close to current price: {tp_price - current_price:.5f} < {min_distance:.5f}"
                else:  # SELL
                    if tp_price >= current_price:
                        return False, f"TP for SELL must be below current price: {tp_price} >= {current_price}"
                    if (current_price - tp_price) < min_distance:
                        return False, f"TP too close to current price: {current_price - tp_price:.5f} < {min_distance:.5f}"
            
            # Validate SL
            if sl_price is not None:
                if action_upper == "BUY":
                    if sl_price >= current_price:
                        return False, f"SL for BUY must be below current price: {sl_price} >= {current_price}"
                    if (current_price - sl_price) < min_distance:
                        return False, f"SL too close to current price: {current_price - sl_price:.5f} < {min_distance:.5f}"
                else:  # SELL
                    if sl_price <= current_price:
                        return False, f"SL for SELL must be above current price: {sl_price} <= {current_price}"
                    if (sl_price - current_price) < min_distance:
                        return False, f"SL too close to current price: {sl_price - current_price:.5f} < {min_distance:.5f}"
            
            return True, "TP/SL levels are valid"
            
        except Exception as e:
            error_msg = f"Error validating TP/SL levels: {str(e)}"
            self.logger.log(f"❌ {error_msg}")
            return False, error_msg
    
    def get_example_inputs(self, unit: str) -> List[str]:
        """Get example inputs for each unit type."""
        examples = {
            "pips": ["20", "15.5", "30pips", "25p"],
            "price": ["1.2050", "1850.25", "0.7500"],
            "%": ["1.5%", "2%", "0.8%"],
            "currency": ["100USD", "50EUR", "200CAD", "10000JPY"]
        }
        return examples.get(unit.lower(), [])