"""
Account Management Module
Handles account information, positions, and currency conversions.
"""

from typing import Optional, Dict, Any, List
import threading

from config import *


class AccountManager:
    """Manages account information and position monitoring."""
    
    def __init__(self, logger):
        """Initialize account manager."""
        self.logger = logger
        self.mt5 = None
        self.account_info = None
        self.account_lock = threading.Lock()
        self._last_update = 0
        self._cache_duration = 1  # Cache for 1 second
        
    def initialize(self, mt5_instance) -> bool:
        """
        Initialize account manager with MT5 instance.
        
        Args:
            mt5_instance: MetaTrader5 instance
            
        Returns:
            bool: True if initialization successful
        """
        try:
            self.mt5 = mt5_instance
            self.update_account_info()
            
            if self.account_info:
                self.logger.log(f"✅ Account Manager initialized")
                self.logger.log(f"👤 Account: {self.account_info['login']}")
                self.logger.log(f"💰 Balance: {self.account_info['balance']}")
                self.logger.log(f"🏢 Company: {self.account_info['company']}")
                return True
            else:
                self.logger.log("❌ Failed to get account information")
                return False
                
        except Exception as e:
            self.logger.log(f"❌ Account Manager initialization failed: {str(e)}")
            return False
    
    def update_account_info(self) -> bool:
        """
        Update account information from MT5.
        
        Returns:
            bool: True if update successful
        """
        with self.account_lock:
            try:
                import time
                current_time = time.time()
                
                # Use cache if recent
                if self.account_info and (current_time - self._last_update) < self._cache_duration:
                    return True
                
                if not self.mt5:
                    return False
                
                account_info = self.mt5.account_info()
                if account_info:
                    self.account_info = {
                        "login": account_info.login,
                        "trade_mode": account_info.trade_mode,
                        "leverage": account_info.leverage,
                        "limit_orders": account_info.limit_orders,
                        "margin_so_mode": account_info.margin_so_mode,
                        "trade_allowed": account_info.trade_allowed,
                        "trade_expert": account_info.trade_expert,
                        "margin_mode": account_info.margin_mode,
                        "currency_digits": account_info.currency_digits,
                        "balance": account_info.balance,
                        "credit": account_info.credit,
                        "profit": account_info.profit,
                        "equity": account_info.equity,
                        "margin": account_info.margin,
                        "margin_free": account_info.margin_free,
                        "margin_level": account_info.margin_level,
                        "margin_so_call": account_info.margin_so_call,
                        "margin_so_so": account_info.margin_so_so,
                        "margin_initial": account_info.margin_initial,
                        "margin_maintenance": account_info.margin_maintenance,
                        "assets": account_info.assets,
                        "liabilities": account_info.liabilities,
                        "commission_blocked": account_info.commission_blocked,
                        "name": account_info.name,
                        "server": account_info.server,
                        "currency": account_info.currency,
                        "company": account_info.company
                    }
                    self._last_update = current_time
                    return True
                else:
                    self.logger.log("❌ Failed to get account info from MT5")
                    return False
                    
            except Exception as e:
                self.logger.log(f"❌ Error updating account info: {str(e)}")
                return False
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current account information.
        
        Returns:
            Dict with account information or None
        """
        self.update_account_info()
        return self.account_info.copy() if self.account_info else None
    
    def get_balance(self) -> float:
        """
        Get current account balance.
        
        Returns:
            float: Account balance
        """
        if self.update_account_info() and self.account_info:
            return self.account_info['balance']
        return 0.0
    
    def get_equity(self) -> float:
        """
        Get current account equity.
        
        Returns:
            float: Account equity
        """
        if self.update_account_info() and self.account_info:
            return self.account_info['equity']
        return 0.0
    
    def get_margin_level(self) -> float:
        """
        Get current margin level.
        
        Returns:
            float: Margin level percentage
        """
        if self.update_account_info() and self.account_info:
            return self.account_info.get('margin_level', 0.0)
        return 0.0
    
    def get_free_margin(self) -> float:
        """
        Get available free margin.
        
        Returns:
            float: Free margin amount
        """
        if self.update_account_info() and self.account_info:
            return self.account_info.get('margin_free', 0.0)
        return 0.0
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions.
        
        Returns:
            List of position dictionaries
        """
        try:
            if not self.mt5:
                return []
            
            positions = self.mt5.positions_get()
            if not positions:
                return []
            
            position_list = []
            for pos in positions:
                position_dict = {
                    "ticket": pos.ticket,
                    "time": pos.time,
                    "type": pos.type,
                    "magic": pos.magic,
                    "identifier": pos.identifier,
                    "reason": pos.reason,
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "sl": pos.sl,
                    "tp": pos.tp,
                    "price_current": pos.price_current,
                    "swap": pos.swap,
                    "profit": pos.profit,
                    "symbol": pos.symbol,
                    "comment": pos.comment,
                    "external_id": pos.external_id
                }
                position_list.append(position_dict)
            
            return position_list
            
        except Exception as e:
            self.logger.log(f"❌ Error getting positions: {str(e)}")
            return []
    
    def get_position_count(self) -> int:
        """
        Get number of open positions.
        
        Returns:
            int: Number of open positions
        """
        return len(self.get_positions())
    
    def get_currency_conversion_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get currency conversion rate between two currencies.
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            float: Conversion rate
        """
        try:
            if from_currency == to_currency:
                return 1.0
            
            # Try direct pair
            symbol = f"{from_currency}{to_currency}"
            tick = self.mt5.symbol_info_tick(symbol)
            if tick and tick.bid > 0:
                return tick.bid
            
            # Try reverse pair
            symbol = f"{to_currency}{from_currency}"
            tick = self.mt5.symbol_info_tick(symbol)
            if tick and tick.ask > 0:
                return 1.0 / tick.ask
            
            # Try cross rate via USD
            if from_currency != "USD" and to_currency != "USD":
                usd_from = self.get_currency_conversion_rate(from_currency, "USD")
                usd_to = self.get_currency_conversion_rate("USD", to_currency)
                if usd_from > 0 and usd_to > 0:
                    return usd_from * usd_to
            
            self.logger.log(f"⚠️ Cannot find conversion rate for {from_currency}/{to_currency}")
            return 1.0  # Fallback to 1:1 rate
            
        except Exception as e:
            self.logger.log(f"❌ Error getting conversion rate {from_currency}/{to_currency}: {str(e)}")
            return 1.0
    
    def calculate_margin_requirement(self, symbol: str, lot_size: float, order_type: int) -> float:
        """
        Calculate margin requirement for a trade.
        
        Args:
            symbol: Trading symbol
            lot_size: Lot size
            order_type: Order type (BUY/SELL)
            
        Returns:
            float: Required margin
        """
        try:
            if not self.mt5:
                return 0.0
            
            # Get symbol info for margin calculation
            symbol_info = self.mt5.symbol_info(symbol)
            if not symbol_info:
                return 0.0
            
            # Get current price
            tick = self.mt5.symbol_info_tick(symbol)
            if not tick:
                return 0.0
            
            price = tick.ask if order_type == self.mt5.ORDER_TYPE_BUY else tick.bid
            
            # Calculate margin
            if symbol_info.trade_contract_size > 0:
                contract_value = lot_size * symbol_info.trade_contract_size * price
                margin = contract_value / self.account_info.get('leverage', 1)
                return margin
            
            return 0.0
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating margin for {symbol}: {str(e)}")
            return 0.0
    
    def is_trading_allowed(self) -> bool:
        """
        Check if trading is allowed on the account.
        
        Returns:
            bool: True if trading is allowed
        """
        if self.update_account_info() and self.account_info:
            return self.account_info.get('trade_allowed', False) and \
                   self.account_info.get('trade_expert', False)
        return False
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive account summary.
        
        Returns:
            Dict with account summary
        """
        if not self.update_account_info() or not self.account_info:
            return {}
        
        positions = self.get_positions()
        total_profit = sum(pos['profit'] for pos in positions)
        
        return {
            "balance": self.account_info['balance'],
            "equity": self.account_info['equity'],
            "margin": self.account_info.get('margin', 0),
            "free_margin": self.account_info.get('margin_free', 0),
            "margin_level": self.account_info.get('margin_level', 0),
            "total_profit": total_profit,
            "open_positions": len(positions),
            "currency": self.account_info['currency'],
            "leverage": self.account_info['leverage'],
            "company": self.account_info['company'],
            "server": self.account_info['server'],
            "trade_allowed": self.account_info.get('trade_allowed', False)
        }
