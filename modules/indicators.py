"""
Technical Indicators Module
Calculates various technical indicators for trading analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import datetime

from config import *


class IndicatorCalculator:
    """Calculates technical indicators from market data."""
    
    def __init__(self, logger, mt5_instance):
        """Initialize indicator calculator."""
        self.logger = logger
        self.mt5 = mt5_instance
        self.indicator_cache = {}
        self.cache_duration = 60  # Cache for 60 seconds
        
    def get_symbol_data(self, symbol: str, timeframe: int = None, count: int = 100) -> Optional[pd.DataFrame]:
        """
        Get historical data for symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: MT5 timeframe (default M1)
            count: Number of bars to retrieve
            
        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            if not self.mt5:
                return None
            
            if timeframe is None:
                timeframe = self.mt5.TIMEFRAME_M1
            
            # Get rates
            rates = self.mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None or len(rates) == 0:
                self.logger.log(f"❌ No rate data for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.log(f"❌ Error getting symbol data for {symbol}: {str(e)}")
            return None
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average.
        
        Args:
            data: Price data series
            period: EMA period
            
        Returns:
            EMA series
        """
        try:
            return data.ewm(span=period, adjust=False).mean()
        except Exception as e:
            self.logger.log(f"❌ Error calculating EMA: {str(e)}")
            return pd.Series()
    
    def calculate_sma(self, data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average.
        
        Args:
            data: Price data series
            period: SMA period
            
        Returns:
            SMA series
        """
        try:
            return data.rolling(window=period).mean()
        except Exception as e:
            self.logger.log(f"❌ Error calculating SMA: {str(e)}")
            return pd.Series()
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            data: Price data series
            period: RSI period
            
        Returns:
            RSI series
        """
        try:
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating RSI: {str(e)}")
            return pd.Series()
    
    def calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Price data series
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line EMA period
            
        Returns:
            Dict with MACD, signal, and histogram series
        """
        try:
            ema_fast = self.calculate_ema(data, fast)
            ema_slow = self.calculate_ema(data, slow)
            
            macd_line = ema_fast - ema_slow
            signal_line = self.calculate_ema(macd_line, signal)
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating MACD: {str(e)}")
            return {}
    
    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: Price data series
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Dict with upper, middle, and lower bands
        """
        try:
            middle = self.calculate_sma(data, period)
            std = data.rolling(window=period).std()
            
            upper = middle + (std * std_dev)
            lower = middle - (std * std_dev)
            
            return {
                'upper': upper,
                'middle': middle,
                'lower': lower
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating Bollinger Bands: {str(e)}")
            return {}
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ATR period
            
        Returns:
            ATR series
        """
        try:
            prev_close = close.shift(1)
            
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            return atr
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating ATR: {str(e)}")
            return pd.Series()
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                           k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        Calculate Stochastic Oscillator.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            k_period: %K period
            d_period: %D period
            
        Returns:
            Dict with %K and %D series
        """
        try:
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            
            return {
                'k': k_percent,
                'd': d_percent
            }
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating Stochastic: {str(e)}")
            return {}
    
    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Williams %R.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: Lookback period
            
        Returns:
            Williams %R series
        """
        try:
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            
            williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
            
            return williams_r
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating Williams %R: {str(e)}")
            return pd.Series()
    
    def calculate_momentum(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Momentum indicator.
        
        Args:
            data: Price data series
            period: Momentum period
            
        Returns:
            Momentum series
        """
        try:
            return data.diff(period)
        except Exception as e:
            self.logger.log(f"❌ Error calculating Momentum: {str(e)}")
            return pd.Series()
    
    def calculate_all_indicators(self, symbol: str, timeframe: int = None) -> Dict[str, Any]:
        """
        Calculate all technical indicators for a symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: MT5 timeframe
            
        Returns:
            Dict with all calculated indicators
        """
        try:
            # Check cache
            cache_key = f"{symbol}_{timeframe}_{int(datetime.datetime.now().timestamp() // self.cache_duration)}"
            if cache_key in self.indicator_cache:
                return self.indicator_cache[cache_key]
            
            # Get market data
            df = self.get_symbol_data(symbol, timeframe)
            if df is None or df.empty:
                return {}
            
            indicators = {}
            
            # Price data
            close = df['close']
            high = df['high']
            low = df['low']
            open_price = df['open']
            volume = df['tick_volume']
            
            # Moving Averages
            indicators['EMA_12'] = self.calculate_ema(close, INDICATOR_PERIODS['EMA_fast']).tolist()
            indicators['EMA_26'] = self.calculate_ema(close, INDICATOR_PERIODS['EMA_slow']).tolist()
            indicators['SMA_20'] = self.calculate_sma(close, 20).tolist()
            
            # Oscillators
            indicators['RSI'] = self.calculate_rsi(close, INDICATOR_PERIODS['RSI']).tolist()
            
            # MACD
            macd_result = self.calculate_macd(close, 
                                            INDICATOR_PERIODS['MACD_fast'],
                                            INDICATOR_PERIODS['MACD_slow'],
                                            INDICATOR_PERIODS['MACD_signal'])
            if macd_result:
                indicators['MACD'] = {
                    'macd': macd_result['macd'].tolist(),
                    'signal': macd_result['signal'].tolist(),
                    'histogram': macd_result['histogram'].tolist()
                }
            
            # Bollinger Bands
            bb_result = self.calculate_bollinger_bands(close, INDICATOR_PERIODS['BB'])
            if bb_result:
                indicators['Bollinger'] = {
                    'upper': bb_result['upper'].tolist(),
                    'middle': bb_result['middle'].tolist(),
                    'lower': bb_result['lower'].tolist()
                }
            
            # ATR
            indicators['ATR'] = self.calculate_atr(high, low, close, INDICATOR_PERIODS['ATR']).tolist()
            
            # Stochastic
            stoch_result = self.calculate_stochastic(high, low, close, 
                                                   INDICATOR_PERIODS['Stochastic_K'],
                                                   INDICATOR_PERIODS['Stochastic_D'])
            if stoch_result:
                indicators['Stochastic'] = {
                    'k': stoch_result['k'].tolist(),
                    'd': stoch_result['d'].tolist()
                }
            
            # Williams %R
            indicators['Williams_R'] = self.calculate_williams_r(high, low, close).tolist()
            
            # Momentum
            indicators['Momentum'] = self.calculate_momentum(close).tolist()
            
            # Additional price-based indicators
            indicators['Price_Data'] = {
                'open': open_price.tolist(),
                'high': high.tolist(),
                'low': low.tolist(),
                'close': close.tolist(),
                'volume': volume.tolist()
            }
            
            # Cache result
            self.indicator_cache[cache_key] = indicators
            
            # Clean old cache entries
            self._clean_cache()
            
            return indicators
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating indicators for {symbol}: {str(e)}")
            return {}
    
    def _clean_cache(self) -> None:
        """Clean old cache entries."""
        try:
            current_time = int(datetime.datetime.now().timestamp() // self.cache_duration)
            
            # Remove entries older than 5 cache periods
            keys_to_remove = []
            for key in self.indicator_cache.keys():
                parts = key.split('_')
                if len(parts) >= 3:
                    try:
                        cache_time = int(parts[-1])
                        if current_time - cache_time > 5:
                            keys_to_remove.append(key)
                    except ValueError:
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.indicator_cache[key]
                
        except Exception as e:
            self.logger.log(f"❌ Error cleaning indicator cache: {str(e)}")
    
    def get_trend_direction(self, symbol: str) -> str:
        """
        Get overall trend direction based on multiple indicators.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            str: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        try:
            indicators = self.calculate_all_indicators(symbol)
            if not indicators:
                return 'NEUTRAL'
            
            signals = []
            
            # EMA trend
            ema_fast = indicators.get('EMA_12', [])
            ema_slow = indicators.get('EMA_26', [])
            if len(ema_fast) >= 2 and len(ema_slow) >= 2:
                if ema_fast[-1] > ema_slow[-1]:
                    signals.append(1)  # Bullish
                else:
                    signals.append(-1)  # Bearish
            
            # RSI
            rsi = indicators.get('RSI', [])
            if len(rsi) >= 1:
                if rsi[-1] > 50:
                    signals.append(1)
                else:
                    signals.append(-1)
            
            # MACD
            macd_data = indicators.get('MACD', {})
            if macd_data and len(macd_data.get('histogram', [])) >= 1:
                if macd_data['histogram'][-1] > 0:
                    signals.append(1)
                else:
                    signals.append(-1)
            
            # Calculate overall signal
            if len(signals) > 0:
                avg_signal = sum(signals) / len(signals)
                if avg_signal > 0.3:
                    return 'BULLISH'
                elif avg_signal < -0.3:
                    return 'BEARISH'
            
            return 'NEUTRAL'
            
        except Exception as e:
            self.logger.log(f"❌ Error determining trend for {symbol}: {str(e)}")
            return 'NEUTRAL'
    
    def get_volatility_measure(self, symbol: str) -> float:
        """
        Get volatility measure for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            float: Volatility measure (ATR-based)
        """
        try:
            indicators = self.calculate_all_indicators(symbol)
            atr_data = indicators.get('ATR', [])
            
            if len(atr_data) >= 1:
                return atr_data[-1]
            else:
                return 0.0
                
        except Exception as e:
            self.logger.log(f"❌ Error calculating volatility for {symbol}: {str(e)}")
            return 0.0
