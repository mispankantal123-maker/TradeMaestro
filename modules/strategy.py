"""
Trading Strategy Module
Implements multiple trading strategies and signal generation.
"""

from typing import Dict, Any, List, Optional, Tuple
import time
import threading

from config import *
from .indicators import IndicatorCalculator
from .orders import OrderManager
from .news_filter import NewsFilter


class StrategyManager:
    """Manages trading strategies and signal generation."""
    
    def __init__(self, logger):
        """Initialize strategy manager."""
        self.logger = logger
        self.mt5 = None
        self.account_manager = None
        self.symbol_manager = None
        self.risk_manager = None
        self.order_manager = None
        self.indicator_calculator = None
        self.news_filter = None
        
        self.current_strategy = "Scalping"
        self.strategy_lock = threading.Lock()
        self.last_signal_time = {}
        
    def initialize(self, mt5_instance, account_manager):
        """
        Initialize strategy manager with required dependencies.
        
        Args:
            mt5_instance: MetaTrader5 instance
            account_manager: Account manager instance
        """
        try:
            self.mt5 = mt5_instance
            self.account_manager = account_manager
            
            # Initialize components
            from .symbols import SymbolManager
            from .risk import RiskManager
            from .orders import OrderManager
            
            self.symbol_manager = SymbolManager(self.logger, 
                                              type('Connection', (), {'mt5': mt5_instance, 'check_connection': lambda: True})())
            self.risk_manager = RiskManager(self.logger, self.symbol_manager, account_manager)
            self.order_manager = OrderManager(self.logger, mt5_instance, self.symbol_manager, 
                                            self.risk_manager, account_manager)
            self.indicator_calculator = IndicatorCalculator(self.logger, mt5_instance)
            self.news_filter = NewsFilter(self.logger)
            
            self.logger.log("✅ Strategy Manager initialized")
            
        except Exception as e:
            self.logger.log(f"❌ Strategy Manager initialization failed: {str(e)}")
    
    def execute_strategy(self, current_session: Dict[str, Any]) -> None:
        """
        Execute the current trading strategy.
        
        Args:
            current_session: Current trading session information
        """
        try:
            with self.strategy_lock:
                if not self._should_trade(current_session):
                    return
                
                # Get preferred symbols for current session
                preferred_symbols = current_session.get('preferred_pairs', POPULAR_SYMBOLS[:5])
                
                for symbol in preferred_symbols:
                    try:
                        self._analyze_and_trade_symbol(symbol, current_session)
                    except Exception as e:
                        self.logger.log(f"❌ Error analyzing {symbol}: {str(e)}")
                        continue
                        
        except Exception as e:
            self.logger.log(f"❌ Error executing strategy: {str(e)}")
    
    def _should_trade(self, current_session: Dict[str, Any]) -> bool:
        """
        Check if trading conditions are favorable.
        
        Args:
            current_session: Current session information
            
        Returns:
            bool: True if should trade
        """
        try:
            # Check if session is active
            if not current_session.get('active', False):
                return False
            
            # Check high-impact news
            if self.news_filter and self.news_filter.is_high_impact_news_time():
                self.logger.log("⚠️ High-impact news time - skipping trades")
                return False
            
            # Check account status
            if self.account_manager and not self.account_manager.is_trading_allowed():
                self.logger.log("⚠️ Trading not allowed on account")
                return False
            
            # Check position limits
            if self.account_manager:
                position_count = self.account_manager.get_position_count()
                if position_count >= MAX_POSITIONS:
                    self.logger.log(f"⚠️ Maximum positions reached: {position_count}")
                    return False
                
                # Check margin level
                margin_level = self.account_manager.get_margin_level()
                if margin_level < 200:  # 200% margin level minimum
                    self.logger.log(f"⚠️ Low margin level: {margin_level}%")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.log(f"❌ Error checking trading conditions: {str(e)}")
            return False
    
    def _analyze_and_trade_symbol(self, symbol: str, current_session: Dict[str, Any]) -> None:
        """
        Analyze symbol and execute trade if signal is found.
        
        Args:
            symbol: Symbol to analyze
            current_session: Current session information
        """
        try:
            # Validate symbol
            if not self.symbol_manager or not self.symbol_manager.validate_and_activate_symbol(symbol):
                return
            
            # Rate limiting per symbol
            current_time = time.time()
            last_trade_time = self.last_signal_time.get(symbol, 0)
            if current_time - last_trade_time < 60:  # 1 minute between signals
                return
            
            # Get market data
            market_data = self._get_market_data(symbol)
            if not market_data:
                return
            
            # Calculate indicators
            indicators = None
            if self.indicator_calculator:
                indicators = self.indicator_calculator.calculate_all_indicators(symbol)
            if not indicators:
                return
            
            # Generate signal
            signal = self._generate_signal(symbol, market_data, indicators, current_session)
            if signal:
                self._execute_trade_signal(signal, current_session)
                self.last_signal_time[symbol] = current_time
                
        except Exception as e:
            self.logger.log(f"❌ Error analyzing symbol {symbol}: {str(e)}")
    
    def _get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current market data for symbol.
        
        Args:
            symbol: Symbol name
            
        Returns:
            Dict with market data or None
        """
        try:
            if not self.symbol_manager:
                return None
                
            tick_data = self.symbol_manager.get_tick_data(symbol)
            if not tick_data:
                return None
            
            symbol_info = self.symbol_manager.get_symbol_info(symbol)
            if not symbol_info:
                return None
            
            return {
                "symbol": symbol,
                "bid": tick_data["bid"],
                "ask": tick_data["ask"],
                "spread": tick_data["spread"],
                "point": symbol_info["point"],
                "digits": symbol_info["digits"]
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error getting market data for {symbol}: {str(e)}")
            return None
    
    def _generate_signal(self, symbol: str, market_data: Dict[str, Any], 
                        indicators: Dict[str, Any], current_session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate trading signal based on strategy and indicators.
        
        Args:
            symbol: Symbol name
            market_data: Current market data
            indicators: Technical indicators
            current_session: Current session info
            
        Returns:
            Signal dictionary or None
        """
        try:
            strategy_name = self.current_strategy
            signal_strength = 0
            signal_type = None
            
            if strategy_name == "HFT":
                signal = self._hft_strategy(symbol, market_data, indicators)
            elif strategy_name == "Scalping":
                signal = self._scalping_strategy(symbol, market_data, indicators)
            elif strategy_name == "Intraday":
                signal = self._intraday_strategy(symbol, market_data, indicators)
            elif strategy_name == "Arbitrage":
                signal = self._arbitrage_strategy(symbol, market_data, indicators)
            else:
                return None
            
            if signal and signal.get('strength', 0) > 0.6:  # Minimum signal strength
                return {
                    "symbol": symbol,
                    "action": signal['action'],
                    "strength": signal['strength'],
                    "strategy": strategy_name,
                    "indicators": indicators,
                    "market_data": market_data
                }
            
            return None
            
        except Exception as e:
            self.logger.log(f"❌ Error generating signal for {symbol}: {str(e)}")
            return None
    
    def _hft_strategy(self, symbol: str, market_data: Dict[str, Any], 
                     indicators: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """High-Frequency Trading strategy implementation."""
        try:
            ema_fast = indicators.get('EMA_12')
            ema_slow = indicators.get('EMA_26')
            rsi = indicators.get('RSI')
            
            if not all([ema_fast, ema_slow, rsi]):
                return None
            
            signal_strength = 0
            action = None
            
            # EMA crossover signal
            if ema_fast and ema_slow and len(ema_fast) >= 2 and len(ema_slow) >= 2:
                if ema_fast[-1] > ema_slow[-1] and ema_fast[-2] <= ema_slow[-2]:
                    # Golden cross
                    signal_strength += 0.4
                    action = "BUY"
                elif ema_fast[-1] < ema_slow[-1] and ema_fast[-2] >= ema_slow[-2]:
                    # Death cross
                    signal_strength += 0.4
                    action = "SELL"
            
            # RSI confirmation
            if rsi and len(rsi) >= 1:
                current_rsi = rsi[-1]
                if action == "BUY" and current_rsi < 70:
                    signal_strength += 0.3
                elif action == "SELL" and current_rsi > 30:
                    signal_strength += 0.3
            
            # Spread filter for HFT
            spread_pips = market_data['spread'] / market_data['point']
            if spread_pips > 2:  # Too wide for HFT
                signal_strength *= 0.5
            
            return {"action": action, "strength": signal_strength} if action else None
            
        except Exception as e:
            self.logger.log(f"❌ Error in HFT strategy: {str(e)}")
            return None
    
    def _scalping_strategy(self, symbol: str, market_data: Dict[str, Any], 
                          indicators: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Scalping strategy implementation."""
        try:
            ema_fast = indicators.get('EMA_12')
            ema_slow = indicators.get('EMA_26')
            rsi = indicators.get('RSI')
            macd = indicators.get('MACD')
            
            if not all([ema_fast, ema_slow, rsi]):
                return None
            
            signal_strength = 0
            action = None
            
            # Multiple timeframe analysis
            if ema_fast and ema_slow and len(ema_fast) >= 3 and len(ema_slow) >= 3:
                # Trend direction
                if ema_fast[-1] > ema_slow[-1]:
                    if market_data['bid'] > ema_fast[-1]:
                        action = "BUY"
                        signal_strength += 0.3
                elif ema_fast[-1] < ema_slow[-1]:
                    if market_data['ask'] < ema_fast[-1]:
                        action = "SELL"
                        signal_strength += 0.3
            
            # RSI momentum
            if rsi and len(rsi) >= 2:
                if action == "BUY" and rsi[-1] > rsi[-2] and rsi[-1] < 65:
                    signal_strength += 0.3
                elif action == "SELL" and rsi[-1] < rsi[-2] and rsi[-1] > 35:
                    signal_strength += 0.3
            
            # MACD confirmation
            if macd and len(macd.get('histogram', [])) >= 2:
                histogram = macd['histogram']
                if action == "BUY" and histogram[-1] > histogram[-2]:
                    signal_strength += 0.2
                elif action == "SELL" and histogram[-1] < histogram[-2]:
                    signal_strength += 0.2
            
            return {"action": action, "strength": signal_strength} if action else None
            
        except Exception as e:
            self.logger.log(f"❌ Error in scalping strategy: {str(e)}")
            return None
    
    def _intraday_strategy(self, symbol: str, market_data: Dict[str, Any], 
                          indicators: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Intraday trading strategy implementation."""
        try:
            ema_fast = indicators.get('EMA_12')
            ema_slow = indicators.get('EMA_26')
            rsi = indicators.get('RSI')
            atr = indicators.get('ATR')
            bollinger = indicators.get('Bollinger')
            
            signal_strength = 0
            action = None
            
            # Trend-following with volatility filter
            if all([ema_fast, ema_slow, atr]) and ema_fast and len(ema_fast) >= 5 and ema_slow and len(ema_slow) >= 5:
                # Strong trend detection
                trend_strength = 0
                for i in range(1, 5):
                    if ema_fast[-i] > ema_slow[-i]:
                        trend_strength += 1
                    else:
                        trend_strength -= 1
                
                if trend_strength >= 3:
                    action = "BUY"
                    signal_strength += 0.4
                elif trend_strength <= -3:
                    action = "SELL"
                    signal_strength += 0.4
            
            # RSI divergence
            if rsi and len(rsi) >= 5:
                if action == "BUY" and rsi[-1] < 60:
                    signal_strength += 0.2
                elif action == "SELL" and rsi[-1] > 40:
                    signal_strength += 0.2
            
            # Bollinger Band position
            if bollinger and len(bollinger['middle']) >= 1:
                current_price = (market_data['bid'] + market_data['ask']) / 2
                if action == "BUY" and current_price < bollinger['lower'][-1]:
                    signal_strength += 0.3
                elif action == "SELL" and current_price > bollinger['upper'][-1]:
                    signal_strength += 0.3
            
            return {"action": action, "strength": signal_strength} if action else None
            
        except Exception as e:
            self.logger.log(f"❌ Error in intraday strategy: {str(e)}")
            return None
    
    def _arbitrage_strategy(self, symbol: str, market_data: Dict[str, Any], 
                           indicators: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Arbitrage strategy implementation."""
        try:
            # Simple spread arbitrage
            spread_pips = market_data['spread'] / market_data['point']
            
            # Look for unusually wide spreads to fade
            if spread_pips > 5:  # Unusual spread
                # Simple mean reversion signal
                return {"action": "BUY", "strength": 0.7}  # Simplified for demo
            
            return None
            
        except Exception as e:
            self.logger.log(f"❌ Error in arbitrage strategy: {str(e)}")
            return None
    
    def _execute_trade_signal(self, signal: Dict[str, Any], current_session: Dict[str, Any]) -> None:
        """
        Execute trade signal by opening position.
        
        Args:
            signal: Trading signal
            current_session: Current session information
        """
        try:
            symbol = signal['symbol']
            action = signal['action']
            strategy_name = signal['strategy']
            
            # Get strategy defaults
            strategy_config = STRATEGY_DEFAULTS.get(strategy_name, STRATEGY_DEFAULTS['Scalping'])
            
            # Apply session adjustments
            session_settings = SESSION_SETTINGS.get(current_session.get('name', 'London'), 
                                                   SESSION_SETTINGS['London'])
            
            # Calculate position parameters
            lot_size = strategy_config['lot_size'] * session_settings.get('lot_multiplier', 1.0)
            tp_pips = strategy_config['tp_pips'] * session_settings.get('tp_multiplier', 1.0)
            sl_pips = strategy_config['sl_pips'] * session_settings.get('sl_multiplier', 1.0)
            
            # Validate position size
            if not self.risk_manager or not self.risk_manager.validate_position_size(symbol, lot_size):
                self.logger.log(f"❌ Invalid position size for {symbol}")
                return
            
            # Execute order
            self.logger.log(f"📈 Executing {action} signal for {symbol} (Strategy: {strategy_name})")
            
            result = None
            if self.order_manager:
                result = self.order_manager.open_order(
                    symbol=symbol,
                    lot_size=lot_size,
                    action=action,
                    sl_input=str(sl_pips),
                    tp_input=str(tp_pips),
                    sl_unit='pips',
                    tp_unit='pips'
                )
            
            if result:
                self.logger.log(f"✅ Order executed successfully for {symbol}")
            else:
                self.logger.log(f"❌ Failed to execute order for {symbol}")
                
        except Exception as e:
            self.logger.log(f"❌ Error executing trade signal: {str(e)}")
    
    def set_strategy(self, strategy_name: str) -> bool:
        """
        Set current trading strategy.
        
        Args:
            strategy_name: Name of strategy to use
            
        Returns:
            bool: True if strategy set successfully
        """
        try:
            if strategy_name in STRATEGY_DEFAULTS:
                with self.strategy_lock:
                    self.current_strategy = strategy_name
                    self.logger.log(f"📊 Strategy changed to: {strategy_name}")
                    return True
            else:
                self.logger.log(f"❌ Unknown strategy: {strategy_name}")
                return False
                
        except Exception as e:
            self.logger.log(f"❌ Error setting strategy: {str(e)}")
            return False
    
    def get_current_strategy(self) -> str:
        """Get current strategy name."""
        return self.current_strategy
    
    def close_all_positions(self) -> bool:
        """
        Close all open positions (emergency function).
        
        Returns:
            bool: True if all positions closed successfully
        """
        try:
            if self.order_manager:
                return self.order_manager.close_all_positions()
            return False
            
        except Exception as e:
            self.logger.log(f"❌ Error closing all positions: {str(e)}")
            return False
