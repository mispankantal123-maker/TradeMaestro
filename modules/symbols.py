"""
Symbol Management Module
Handles symbol validation, activation, and market data operations.
"""

import time
from typing import List, Optional, Dict, Any, Tuple
import threading

from config import *


class SymbolManager:
    """Manages symbol validation, activation, and market data access."""
    
    def __init__(self, logger, connection):
        """Initialize symbol manager."""
        self.logger = logger
        self.connection = connection
        self.mt5 = connection.mt5
        self.symbol_cache = {}
        self.symbol_lock = threading.Lock()
        
    def get_symbols(self) -> List[str]:
        """
        Get list of available symbols from MT5.
        
        Returns:
            List of symbol names
        """
        try:
            if not self.connection.check_connection():
                self.logger.log("❌ No MT5 connection for symbol retrieval")
                return []
            
            symbols = self.mt5.symbols_get()
            if symbols:
                symbol_names = [symbol.name for symbol in symbols if symbol.visible]
                self.logger.log(f"📊 Retrieved {len(symbol_names)} visible symbols")
                return symbol_names
            else:
                self.logger.log("⚠️ No symbols available")
                return []
                
        except Exception as e:
            self.logger.log(f"❌ Error getting symbols: {str(e)}")
            return []
    
    def get_symbol_suggestions(self) -> List[str]:
        """
        Get suggested popular symbols for fallback.
        
        Returns:
            List of popular symbol names
        """
        return POPULAR_SYMBOLS.copy()
    
    def validate_and_activate_symbol(self, symbol: str) -> bool:
        """
        Comprehensive symbol validation and activation with multiple variations.
        
        Args:
            symbol: Symbol name to validate and activate
            
        Returns:
            bool: True if symbol is valid and activated
        """
        with self.symbol_lock:
            try:
                if not self.connection.check_connection():
                    self.logger.log("❌ No MT5 connection for symbol validation")
                    return False
                
                # Check cache first
                if symbol in self.symbol_cache:
                    return self.symbol_cache[symbol]
                
                # Try original symbol first
                if self._test_symbol(symbol):
                    self.symbol_cache[symbol] = True
                    return True
                
                # Try symbol variations
                variations = self._generate_symbol_variations(symbol)
                
                for variation in variations:
                    self.logger.log(f"🔄 Testing symbol variation: {variation}")
                    if self._test_symbol(variation):
                        self.logger.log(f"✅ Symbol activated: {variation}")
                        self.symbol_cache[symbol] = True
                        return True
                
                # Special handling for gold symbols
                if symbol.upper() in ["GOLD", "XAU", "XAUUSD"]:
                    gold_symbol = self.detect_gold_symbol()
                    if gold_symbol:
                        self.logger.log(f"✅ Gold symbol detected: {gold_symbol}")
                        self.symbol_cache[symbol] = True
                        return True
                
                self.logger.log(f"❌ Symbol not found: {symbol}")
                self.symbol_cache[symbol] = False
                return False
                
            except Exception as e:
                self.logger.log(f"❌ Error validating symbol {symbol}: {str(e)}")
                self.symbol_cache[symbol] = False
                return False
    
    def _generate_symbol_variations(self, symbol: str) -> List[str]:
        """
        Generate possible symbol variations for different brokers.
        
        Args:
            symbol: Base symbol name
            
        Returns:
            List of symbol variations
        """
        variations = []
        base_symbol = symbol.upper()
        
        # Common variations
        variations.extend([
            base_symbol,
            f"{base_symbol}.m",
            f"{base_symbol}.raw", 
            f"{base_symbol}_m",
            f"{base_symbol}-m",
            base_symbol.replace("/", ""),
            base_symbol.replace("-", ""),
        ])
        
        # Add slash variations for forex pairs
        if len(base_symbol) == 6 and base_symbol.isalpha():
            variations.append(f"{base_symbol[:3]}/{base_symbol[3:]}")
            variations.append(f"{base_symbol[:3]}-{base_symbol[3:]}")
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(variations))
    
    def _test_symbol(self, symbol: str) -> bool:
        """
        Test if a symbol is valid and can be activated.
        
        Args:
            symbol: Symbol to test
            
        Returns:
            bool: True if symbol is valid and activated
        """
        try:
            # Get symbol info
            symbol_info = self.mt5.symbol_info(symbol)
            if not symbol_info:
                return False
            
            # Activate symbol if not visible
            if not symbol_info.visible:
                if not self.mt5.symbol_select(symbol, True):
                    self.logger.log(f"⚠️ Failed to activate symbol: {symbol}")
                    return False
                time.sleep(0.1)  # Brief pause for activation
            
            # Test tick data access
            for attempt in range(MAX_SYMBOL_TEST_ATTEMPTS):
                tick = self.mt5.symbol_info_tick(symbol)
                if tick and tick.bid > 0 and tick.ask > 0:
                    self.logger.log(f"✅ Symbol validated: {symbol} (Bid: {tick.bid}, Ask: {tick.ask})")
                    
                    # Check trading mode
                    if symbol_info.trade_mode == self.mt5.SYMBOL_TRADE_MODE_DISABLED:
                        self.logger.log(f"⚠️ Trading disabled for symbol: {symbol}")
                        return False
                    
                    # Check spread
                    spread = (tick.ask - tick.bid) / symbol_info.point
                    if self._is_spread_acceptable(symbol, spread):
                        return True
                    else:
                        self.logger.log(f"⚠️ Spread too high for {symbol}: {spread}")
                        return False
                
                time.sleep(0.1)
            
            self.logger.log(f"❌ No valid tick data for symbol: {symbol}")
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error testing symbol {symbol}: {str(e)}")
            return False
    
    def _is_spread_acceptable(self, symbol: str, spread: float) -> bool:
        """
        Check if spread is acceptable for the symbol type.
        
        Args:
            symbol: Symbol name
            spread: Current spread in pips
            
        Returns:
            bool: True if spread is acceptable
        """
        symbol_upper = symbol.upper()
        
        # Determine symbol type and check threshold
        if any(pair in symbol_upper for pair in FOREX_MAJOR):
            threshold = SPREAD_THRESHOLDS["forex_major"]
        elif "JPY" in symbol_upper:
            threshold = SPREAD_THRESHOLDS["jpy_pairs"]
        elif any(metal in symbol_upper for metal in ["XAU", "GOLD"]):
            threshold = SPREAD_THRESHOLDS["gold"]
        elif any(metal in symbol_upper for metal in ["XAG", "SILVER"]):
            threshold = SPREAD_THRESHOLDS["silver"]
        elif "OIL" in symbol_upper:
            threshold = SPREAD_THRESHOLDS["oil"]
        elif any(crypto in symbol_upper for crypto in CRYPTOCURRENCIES):
            threshold = SPREAD_THRESHOLDS["crypto"]
        elif any(idx in symbol_upper for idx in INDICES):
            threshold = SPREAD_THRESHOLDS["indices"]
        else:
            threshold = SPREAD_THRESHOLDS["forex_minor"]
        
        return spread <= threshold
    
    def detect_gold_symbol(self) -> Optional[str]:
        """
        Auto-detect the correct gold symbol for the broker.
        
        Returns:
            str or None: Valid gold symbol if found
        """
        try:
            for gold_variation in GOLD_SYMBOL_VARIATIONS:
                if self._test_symbol(gold_variation):
                    self.logger.log(f"🥇 Gold symbol detected: {gold_variation}")
                    return gold_variation
            
            self.logger.log("❌ No valid gold symbol found")
            return None
            
        except Exception as e:
            self.logger.log(f"❌ Error detecting gold symbol: {str(e)}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive symbol information.
        
        Args:
            symbol: Symbol name
            
        Returns:
            Dict with symbol information or None
        """
        try:
            if not self.connection.check_connection():
                return None
            
            symbol_info = self.mt5.symbol_info(symbol)
            if not symbol_info:
                return None
            
            tick_info = self.mt5.symbol_info_tick(symbol)
            
            info = {
                "name": symbol_info.name,
                "description": symbol_info.description,
                "digits": symbol_info.digits,
                "point": symbol_info.point,
                "trade_mode": symbol_info.trade_mode,
                "volume_min": symbol_info.volume_min,
                "volume_max": symbol_info.volume_max,
                "volume_step": symbol_info.volume_step,
                "currency_base": symbol_info.currency_base,
                "currency_profit": symbol_info.currency_profit,
                "currency_margin": symbol_info.currency_margin,
                "visible": symbol_info.visible,
                "trade_tick_value": symbol_info.trade_tick_value,
                "trade_tick_size": symbol_info.trade_tick_size,
            }
            
            if tick_info:
                info.update({
                    "bid": tick_info.bid,
                    "ask": tick_info.ask,
                    "spread": (tick_info.ask - tick_info.bid) / symbol_info.point,
                    "time": tick_info.time
                })
            
            return info
            
        except Exception as e:
            self.logger.log(f"❌ Error getting symbol info for {symbol}: {str(e)}")
            return None
    
    def get_tick_data(self, symbol: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Get current tick data for symbol with retries.
        
        Args:
            symbol: Symbol name
            retries: Number of retry attempts
            
        Returns:
            Dict with tick data or None
        """
        try:
            for attempt in range(retries):
                if not self.connection.check_connection():
                    return None
                
                tick = self.mt5.symbol_info_tick(symbol)
                if tick and tick.bid > 0 and tick.ask > 0:
                    return {
                        "symbol": symbol,
                        "bid": tick.bid,
                        "ask": tick.ask,
                        "last": tick.last,
                        "volume": tick.volume,
                        "time": tick.time,
                        "spread": tick.ask - tick.bid
                    }
                
                if attempt < retries - 1:
                    time.sleep(0.1)
            
            self.logger.log(f"❌ Failed to get tick data for {symbol}")
            return None
            
        except Exception as e:
            self.logger.log(f"❌ Error getting tick data for {symbol}: {str(e)}")
            return None
    
    def is_market_open(self, symbol: str) -> bool:
        """
        Check if market is open for trading for the given symbol.
        
        Args:
            symbol: Symbol name
            
        Returns:
            bool: True if market is open
        """
        try:
            tick_data = self.get_tick_data(symbol)
            if not tick_data:
                return False
            
            # Check if we have recent tick data (within last 5 minutes)
            import datetime
            current_time = datetime.datetime.now().timestamp()
            tick_time = tick_data["time"]
            
            return (current_time - tick_time) < 300  # 5 minutes
            
        except Exception as e:
            self.logger.log(f"❌ Error checking market status for {symbol}: {str(e)}")
            return False
