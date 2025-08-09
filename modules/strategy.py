"""
Trading Strategy Module
Implements multiple trading strategies and signal generation.
"""

from typing import Dict, Any, List, Optional, Tuple
import time
import threading
import pandas as pd

from config import *
from .indicators import IndicatorCalculator
from .orders import OrderManager
from .news_filter import NewsFilter
from .ai_analysis import AIMarketAnalyzer
from .tp_sl_parser import TPSLParser
from .complete_strategy import CompleteStrategyEngine


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
        self.ai_analyzer = None
        self.tp_sl_parser = None
        self.gui = None  # GUI reference for parameter retrieval
        
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
            self.ai_analyzer = AIMarketAnalyzer(self.logger)
            self.tp_sl_parser = TPSLParser(self.logger, self.symbol_manager, account_manager)
            self.strategy_engine = CompleteStrategyEngine(self.logger, self.ai_analyzer)
            
            self.logger.log("✅ Strategy Manager initialized with AI enhancement")
            
        except Exception as e:
            self.logger.log(f"❌ Strategy Manager initialization failed: {str(e)}")
    
    def execute_strategy(self, current_session: Dict[str, Any]) -> None:
        """
        Execute the current trading strategy with batch processing and profiling.
        
        Args:
            current_session: Current trading session information
        """
        try:
            exec_start = time.time()
            self.logger.log(f"[STRATEGY] Executing {self.current_strategy} strategy...")
            
            with self.strategy_lock:
                if not self._should_trade(current_session):
                    return
                
                # Get preferred symbols for current session (BATCHED processing)
                preferred_symbols = current_session.get('preferred_pairs', POPULAR_SYMBOLS[:5])
                
                # Batch processing: Process symbols in smaller batches to prevent blocking
                batch_size = 2  # Process 2 symbols per batch
                total_symbols = len(preferred_symbols)
                
                for i in range(0, total_symbols, batch_size):
                    batch_start = time.time()
                    batch = preferred_symbols[i:i + batch_size]
                    
                    self.logger.log(f"[STRATEGY] Processing batch {i//batch_size + 1}/{(total_symbols + batch_size - 1)//batch_size}: {batch}")
                    
                    for symbol in batch:
                        try:
                            symbol_start = time.time()
                            self._analyze_and_trade_symbol_with_timeout(symbol, current_session)
                            symbol_elapsed = time.time() - symbol_start
                            
                            # Log slow symbol analysis
                            if symbol_elapsed > 2.0:
                                self.logger.log(f"⚠️ Slow analysis for {symbol}: {symbol_elapsed:.3f}s")
                                
                        except Exception as e:
                            self.logger.log(f"❌ Error analyzing {symbol}: {str(e)}")
                            continue
                    
                    batch_elapsed = time.time() - batch_start
                    self.logger.log(f"[STRATEGY] Batch completed in {batch_elapsed:.3f}s")
                    
                    # FREEZE FIX #4: Yield control between batches with progress check
                    time.sleep(0.1)
                    
                    # Additional yield for GUI responsiveness on Windows
                    if hasattr(self, 'gui') and self.gui and hasattr(self.gui, 'root'):
                        try:
                            self.gui.root.update_idletasks()  # Allow GUI to update
                        except:
                            pass
                
                total_elapsed = time.time() - exec_start
                self.logger.log(f"[STRATEGY] ✅ Strategy execution completed in {total_elapsed:.3f}s")
                        
        except Exception as e:
            self.logger.log(f"❌ Error executing strategy: {str(e)}")
    
    def _analyze_and_trade_symbol_with_timeout(self, symbol: str, current_session: Dict[str, Any], timeout: int = 5) -> None:
        """
        Analyze symbol with timeout to prevent hanging.
        
        Args:
            symbol: Trading symbol to analyze
            current_session: Current session information
            timeout: Maximum execution time in seconds
        """
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Symbol analysis timeout for {symbol}")
            
            # Set timeout alarm (Unix-only, fallback for other systems)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)
                
                # Execute the analysis
                self._analyze_and_trade_symbol(symbol, current_session)
                
            finally:
                signal.alarm(0)  # Cancel the alarm
                
        except TimeoutError as e:
            self.logger.log(f"⚠️ {str(e)}")
        except Exception as e:
            # Fallback for systems without signal support
            self._analyze_and_trade_symbol(symbol, current_session)
    
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
        Analyze symbol and execute trades based on current strategy.
        
        Args:
            symbol: Trading symbol to analyze
            current_session: Current session information
        """
        try:
            # Check if we've traded this symbol recently
            current_time = time.time()
            if symbol in self.last_signal_time:
                time_since_last = current_time - self.last_signal_time[symbol]
                min_interval = STRATEGY_INTERVALS.get(self.current_strategy, 60)
                if time_since_last < min_interval:
                    return
            
            # Get market data with sufficient history for analysis
            data = self.indicator_calculator.get_symbol_data(symbol, count=200)
            if data is None or len(data) < 50:
                self.logger.log(f"❌ Insufficient data for {symbol}: {len(data) if data is not None else 0} bars")
                return
            
            # Calculate all indicators needed for strategies
            data = self.indicator_calculator.calculate_all_indicators(data)
            
            # Run the complete strategy analysis with AI enhancement
            action, signals = self.strategy_engine.run_complete_strategy(self.current_strategy, data, symbol)
            
            if action and action in ['BUY', 'SELL']:
                # Get parameters from GUI (NOT hardcoded from config!)
                current_price = data['close'].iloc[-1]
                
                if self.gui:
                    # Get GUI parameters (exact bobot2.py integration)
                    lot_size = self.gui.get_current_lot()
                    tp_value = self.gui.get_current_tp()
                    sl_value = self.gui.get_current_sl()
                    tp_unit = self.gui.get_current_tp_unit()
                    sl_unit = self.gui.get_current_sl_unit()
                else:
                    # Fallback if no GUI (headless mode)
                    lot_size = STRATEGY_DEFAULTS[self.current_strategy]['lot_size']
                    tp_value = str(STRATEGY_DEFAULTS[self.current_strategy]['tp_pips'])
                    sl_value = str(STRATEGY_DEFAULTS[self.current_strategy]['sl_pips'])
                    tp_unit = "pips"
                    sl_unit = "pips"
                
                # Parse TP/SL using multi-unit parser (exact bobot2.py functionality)
                tp_price = None
                sl_price = None
                
                if tp_value and tp_value.strip():
                    tp_price = self.tp_sl_parser.parse_tp_sl_input(
                        tp_value, tp_unit, symbol, current_price, action)
                
                if sl_value and sl_value.strip():
                    sl_price = self.tp_sl_parser.parse_tp_sl_input(
                        sl_value, sl_unit, symbol, current_price, 
                        "SELL" if action == "BUY" else "BUY")  # Opposite for SL
                
                # Validate TP/SL levels
                is_valid, error_msg = self.tp_sl_parser.validate_tp_sl_levels(
                    symbol, current_price, tp_price, sl_price, action)
                
                if not is_valid:
                    self.logger.log(f"❌ Invalid TP/SL levels for {symbol}: {error_msg}")
                    return
                
                # Execute trade with enhanced parameters
                result = self.order_manager.place_order(
                    symbol=symbol,
                    action=action,
                    volume=lot_size,
                    tp_price=tp_price,
                    sl_price=sl_price,
                    comment=f"{self.current_strategy}_AI_Signal"
                )
                
                if result:
                    self.last_signal_time[symbol] = current_time
                    self.logger.log(f"✅ {self.current_strategy} trade executed: {action} {symbol}")
                    for signal in signals:
                        self.logger.log(f"   📊 {signal}")
                else:
                    self.logger.log(f"❌ Trade execution failed for {symbol}")
        
        except Exception as e:
            self.logger.log(f"❌ Error analyzing symbol {symbol}: {str(e)}")
    
    def set_gui_reference(self, gui_instance):
        """Set GUI reference for parameter retrieval (exact bobot2.py integration)."""
        self.gui = gui_instance
        self.logger.log("✅ GUI reference set for strategy manager")
    
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
    
    def _run_complete_strategy(self, strategy: str, df: pd.DataFrame, symbol: str) -> Tuple[Optional[str], List[str]]:
        """Complete strategy analysis based on bobot2.py implementation"""
        try:
            if len(df) < 50:
                self.logger.log(f"❌ Insufficient data for {symbol}: {len(df)} bars (need 50+)")
                return None, []
            
            # Get precision info
            digits = 5  # Default for most forex pairs
            point = 0.00001  # Default point value
            
            # Use most recent candle data
            last = df.iloc[-1]
            prev = df.iloc[-2]
            prev2 = df.iloc[-3] if len(df) > 3 else prev
            
            # Get current prices
            current_price = last['close']
            last_close = last['close']
            last_high = last['high']
            last_low = last['low']
            last_open = last['open']
            
            action = None
            signals = []
            buy_signals = 0
            sell_signals = 0
            
            # Enhanced price logging
            self.logger.log(f"📊 {symbol} Data: O={last_open:.5f} H={last_high:.5f} L={last_low:.5f} C={last_close:.5f}")
            
            if strategy == "Scalping":
                # Enhanced Scalping strategy from bobot2.py
                self.logger.log("⚡ Scalping: Multi-confirmation EMA system...")
                
                # Get EMA values
                ema5_current = last.get('EMA5', current_price)
                ema8_current = last.get('EMA8', current_price)
                ema13_current = last.get('EMA13', current_price)
                ema50_current = last.get('EMA50', current_price)
                
                ema5_prev = prev.get('EMA5', current_price)
                ema8_prev = prev.get('EMA8', current_price)
                ema13_prev = prev.get('EMA13', current_price)
                
                self.logger.log(f"🔍 Scalping EMAs: 5={ema5_current:.5f}, 8={ema8_current:.5f}, 13={ema13_current:.5f}")
                
                # EMA crossover detection
                min_cross_threshold = point * 2
                ema5_cross_up = (ema5_current > ema13_current and ema5_prev <= ema13_prev and
                               abs(ema5_current - ema13_current) >= min_cross_threshold)
                ema5_cross_down = (ema5_current < ema13_current and ema5_prev >= ema13_prev and
                                 abs(ema5_current - ema13_current) >= min_cross_threshold)
                
                # Trend confirmation
                trend_bullish = (ema5_current > ema13_current > ema50_current and current_price > ema50_current)
                trend_bearish = (ema5_current < ema13_current < ema50_current and current_price < ema50_current)
                
                # Price action confirmation
                candle_body = abs(last_close - last_open)
                candle_range = last_high - last_low
                candle_body_ratio = candle_body / max(candle_range, point) if candle_range > 0 else 0
                
                bullish_candle = last_close > last_open and candle_body_ratio > 0.3
                bearish_candle = last_close < last_open and candle_body_ratio > 0.3
                
                # RSI analysis
                rsi_value = last.get('RSI', 50)
                rsi_bullish = 35 < rsi_value < 75
                rsi_bearish = 25 < rsi_value < 65
                
                # BUY SIGNALS
                if ema5_cross_up:
                    if trend_bullish and bullish_candle:
                        if rsi_value < 30 and rsi_value > prev.get('RSI', 50):
                            buy_signals += 8
                            signals.append(f"✅ SCALP STRONG: EMA cross UP + RSI recovery @ {current_price:.5f}")
                        elif rsi_bullish and current_price > ema50_current:
                            buy_signals += 6
                            signals.append(f"✅ SCALP: EMA cross UP + trend @ {current_price:.5f}")
                    else:
                        buy_signals += 4
                        signals.append(f"✅ SCALP: EMA cross UP + basic conditions @ {current_price:.5f}")
                
                # Price above EMA5 continuation
                elif (current_price > ema5_current and ema5_current > ema13_current and
                      current_price > last_high * 0.999):
                    if (rsi_value > 50 and last.get('MACD_histogram', 0) > prev.get('MACD_histogram', 0)):
                        buy_signals += 5
                        signals.append(f"✅ SCALP: Uptrend continuation @ {current_price:.5f}")
                    elif current_price > ema50_current:
                        buy_signals += 3
                        signals.append(f"✅ SCALP: Basic uptrend @ {current_price:.5f}")
                
                # SELL SIGNALS
                if ema5_cross_down:
                    if trend_bearish and bearish_candle:
                        if rsi_value > 70 and rsi_value < prev.get('RSI', 50):
                            sell_signals += 8
                            signals.append(f"✅ SCALP STRONG: EMA cross DOWN + RSI decline @ {current_price:.5f}")
                        elif rsi_bearish and current_price < ema50_current:
                            sell_signals += 6
                            signals.append(f"✅ SCALP: EMA cross DOWN + trend @ {current_price:.5f}")
                    else:
                        sell_signals += 4
                        signals.append(f"✅ SCALP: EMA cross DOWN + basic conditions @ {current_price:.5f}")
                
                # Price below EMA5 continuation
                elif (current_price < ema5_current and ema5_current < ema13_current and
                      current_price < last_low * 1.001):
                    if (rsi_value < 50 and last.get('MACD_histogram', 0) < prev.get('MACD_histogram', 0)):
                        sell_signals += 5
                        signals.append(f"✅ SCALP: Downtrend continuation @ {current_price:.5f}")
                    elif current_price < ema50_current:
                        sell_signals += 3
                        signals.append(f"✅ SCALP: Basic downtrend @ {current_price:.5f}")
                
                # RSI Extreme Levels
                if rsi_value < 25:
                    buy_signals += 2
                    signals.append(f"✅ SCALP: RSI oversold ({rsi_value:.1f})")
                elif rsi_value > 75:
                    sell_signals += 2
                    signals.append(f"✅ SCALP: RSI overbought ({rsi_value:.1f})")
                
                # MACD momentum
                if (last.get('MACD_histogram', 0) > 0 and
                        last.get('MACD_histogram', 0) > prev.get('MACD_histogram', 0)):
                    buy_signals += 2
                    signals.append("✅ SCALP: MACD momentum bullish")
                elif (last.get('MACD_histogram', 0) < 0 and
                      last.get('MACD_histogram', 0) < prev.get('MACD_histogram', 0)):
                    sell_signals += 2
                    signals.append("✅ SCALP: MACD momentum bearish")
            
            elif strategy == "HFT":
                # High-Frequency Trading strategy
                self.logger.log("⚡ HFT: Tick-based precision trading...")
                
                # Enhanced HFT logic from bobot2.py
                ema5 = last.get('EMA5', current_price)
                ema8 = last.get('EMA8', current_price)
                rsi = last.get('RSI', 50)
                
                # Tick momentum
                price_change = current_price - prev['close']
                momentum = price_change / point if point > 0 else 0
                
                # HFT signals based on micro-movements
                if momentum > 5 and ema5 > ema8 and rsi < 70:
                    buy_signals += 6
                    signals.append(f"✅ HFT: Strong upward momentum ({momentum:.1f} points)")
                elif momentum < -5 and ema5 < ema8 and rsi > 30:
                    sell_signals += 6
                    signals.append(f"✅ HFT: Strong downward momentum ({momentum:.1f} points)")
                elif momentum > 3 and ema5 > ema8:
                    buy_signals += 4
                    signals.append(f"✅ HFT: Moderate upward momentum ({momentum:.1f} points)")
                elif momentum < -3 and ema5 < ema8:
                    sell_signals += 4
                    signals.append(f"✅ HFT: Moderate downward momentum ({momentum:.1f} points)")
            
            elif strategy == "Intraday":
                # Intraday strategy with MACD and trend analysis
                self.logger.log("📈 Intraday: MACD + trend analysis...")
                
                macd = last.get('MACD', 0)
                macd_signal = last.get('MACD_signal', 0)
                macd_hist = last.get('MACD_histogram', 0)
                ema20 = last.get('EMA20', current_price)
                ema50 = last.get('EMA50', current_price)
                rsi = last.get('RSI', 50)
                
                # MACD crossover
                macd_prev = prev.get('MACD', 0)
                macd_signal_prev = prev.get('MACD_signal', 0)
                
                macd_bullish_cross = macd > macd_signal and macd_prev <= macd_signal_prev
                macd_bearish_cross = macd < macd_signal and macd_prev >= macd_signal_prev
                
                # Trend confirmation
                strong_uptrend = ema20 > ema50 and current_price > ema20
                strong_downtrend = ema20 < ema50 and current_price < ema20
                
                # Intraday signals
                if macd_bullish_cross and strong_uptrend and 30 < rsi < 70:
                    buy_signals += 7
                    signals.append("✅ INTRADAY: MACD bullish cross + uptrend")
                elif macd_bearish_cross and strong_downtrend and 30 < rsi < 70:
                    sell_signals += 7
                    signals.append("✅ INTRADAY: MACD bearish cross + downtrend")
                elif macd_hist > 0 and macd_hist > prev.get('MACD_histogram', 0) and strong_uptrend:
                    buy_signals += 5
                    signals.append("✅ INTRADAY: MACD momentum + uptrend")
                elif macd_hist < 0 and macd_hist < prev.get('MACD_histogram', 0) and strong_downtrend:
                    sell_signals += 5
                    signals.append("✅ INTRADAY: MACD momentum + downtrend")
            
            elif strategy == "Arbitrage":
                # Arbitrage strategy with mean reversion
                self.logger.log("🔄 Arbitrage: Mean reversion analysis...")
                
                # Bollinger Bands for mean reversion
                bb_upper = last.get('BB_upper', current_price * 1.001)
                bb_lower = last.get('BB_lower', current_price * 0.999)
                bb_middle = last.get('BB_middle', current_price)
                rsi = last.get('RSI', 50)
                
                # Mean reversion signals
                if current_price <= bb_lower and rsi < 30:
                    buy_signals += 6
                    signals.append("✅ ARBITRAGE: Price at lower BB + oversold")
                elif current_price >= bb_upper and rsi > 70:
                    sell_signals += 6
                    signals.append("✅ ARBITRAGE: Price at upper BB + overbought")
                elif current_price < bb_middle and rsi < 40:
                    buy_signals += 4
                    signals.append("✅ ARBITRAGE: Below middle BB + oversold")
                elif current_price > bb_middle and rsi > 60:
                    sell_signals += 4
                    signals.append("✅ ARBITRAGE: Above middle BB + overbought")
            
            # Signal threshold based on strategy
            thresholds = {"Scalping": 5, "HFT": 4, "Intraday": 5, "Arbitrage": 4}
            threshold = thresholds.get(strategy, 5)
            
            # Determine final action
            if buy_signals >= threshold and buy_signals > sell_signals:
                action = "BUY"
                self.logger.log(f"🟢 {strategy} BUY signal: {buy_signals} points")
            elif sell_signals >= threshold and sell_signals > buy_signals:
                action = "SELL"
                self.logger.log(f"🔴 {strategy} SELL signal: {sell_signals} points")
            else:
                self.logger.log(f"⚪ {strategy} No signal: BUY={buy_signals}, SELL={sell_signals}")
            
            return action, signals
            
        except Exception as e:
            self.logger.log(f"❌ Error in strategy analysis: {str(e)}")
            return None, []
    
    def set_strategy(self, strategy_name: str) -> bool:
        """
        Set the current trading strategy.
        
        Args:
            strategy_name: Name of the strategy to set
            
        Returns:
            bool: True if strategy was set successfully
        """
        try:
            if strategy_name in STRATEGY_DEFAULTS:
                self.current_strategy = strategy_name
                self.logger.log(f"✅ Strategy changed to: {strategy_name}")
                return True
            else:
                self.logger.log(f"❌ Unknown strategy: {strategy_name}")
                return False
        except Exception as e:
            self.logger.log(f"❌ Error setting strategy: {str(e)}")
            return False
    
    def set_gui_reference(self, gui_instance):
        """Set GUI reference for parameter access (exact bobot2.py integration)"""
        try:
            self.gui = gui_instance
            self.logger.log("✅ GUI reference set for strategy manager")
        except Exception as e:
            self.logger.log(f"❌ Error setting GUI reference: {str(e)}")
            return False
    
    def get_current_strategy(self) -> str:
        """Get the current trading strategy."""
        return self.current_strategy
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategies."""
        return list(STRATEGY_DEFAULTS.keys())
    
    def close_all_positions(self) -> bool:
        """
        Close all open positions (emergency function).
        
        Returns:
            bool: True if all positions closed successfully
        """
        try:
            if not self.order_manager:
                self.logger.log("❌ Order manager not available")
                return False
            
            self.logger.log("🚨 EMERGENCY: Closing all positions...")
            
            # Get all open positions
            if hasattr(self.order_manager, 'close_all_positions'):
                result = self.order_manager.close_all_positions()
                if result:
                    self.logger.log("✅ All positions closed successfully")
                    return True
                else:
                    self.logger.log("❌ Failed to close some positions")
                    return False
            else:
                self.logger.log("❌ Close all positions function not available")
                return False
                
        except Exception as e:
            self.logger.log(f"❌ Error closing all positions: {str(e)}")
            return False
    
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
