"""
Complete Strategy Implementation Module
Implements the full signal generation system from bobot2.py with AI enhancement
Combines all indicators, patterns, and AI analysis for high-quality signals
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from config import *


class CompleteStrategyEngine:
    """Complete strategy engine with AI-enhanced signal generation from bobot2.py."""
    
    def __init__(self, logger, ai_analyzer):
        """Initialize complete strategy engine."""
        self.logger = logger
        self.ai_analyzer = ai_analyzer
        
    def run_complete_strategy(self, strategy: str, data: pd.DataFrame, symbol: str) -> Tuple[Optional[str], List[str]]:
        """
        Run complete strategy analysis with AI enhancement from bobot2.py.
        
        Args:
            strategy: Strategy name ("HFT", "Scalping", "Intraday", "Arbitrage")
            data: OHLCV DataFrame with all indicators calculated
            symbol: Trading symbol
            
        Returns:
            Tuple of (action, signals_list)
        """
        try:
            if len(data) < 50:
                return None, ["❌ Insufficient data for strategy analysis"]
            
            # Get current market data
            last = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else last
            current_price = last['close']
            
            # Initialize signal tracking
            buy_signals = 0
            sell_signals = 0
            signals = []
            
            # Get AI market analysis first
            market_analysis = self.ai_analyzer.analyze_market_structure(data, symbol)
            
            # Strategy-specific signal generation
            if strategy == "HFT":
                buy_signals, sell_signals, signals = self._generate_hft_signals(
                    data, buy_signals, sell_signals, signals, market_analysis)
                    
            elif strategy == "Scalping":
                buy_signals, sell_signals, signals = self._generate_scalping_signals(
                    data, buy_signals, sell_signals, signals, market_analysis)
                    
            elif strategy == "Intraday":
                buy_signals, sell_signals, signals = self._generate_intraday_signals(
                    data, buy_signals, sell_signals, signals, market_analysis)
                    
            elif strategy == "Arbitrage":
                buy_signals, sell_signals, signals = self._generate_arbitrage_signals(
                    data, buy_signals, sell_signals, signals, market_analysis)
            
            # Calculate signal quality score
            quality_score = self.ai_analyzer.calculate_signal_quality_score(
                data, signals, market_analysis)
            
            # AI-enhanced signal boosting
            enhanced_signals, ai_buy, ai_sell = self.ai_analyzer.enhance_signals_with_ai(
                data, signals, market_analysis, strategy)
            
            buy_signals += ai_buy
            sell_signals += ai_sell
            signals = enhanced_signals
            
            # Determine minimum signal threshold based on strategy and session
            min_threshold = self._get_signal_threshold(strategy, quality_score)
            
            # Final decision logic
            action = None
            if buy_signals >= min_threshold and buy_signals > sell_signals:
                action = "BUY"
                self.logger.log(f"🟢 {strategy} BUY signal: {buy_signals} vs {sell_signals} (Quality: {quality_score}%)")
            elif sell_signals >= min_threshold and sell_signals > buy_signals:
                action = "SELL"
                self.logger.log(f"🔴 {strategy} SELL signal: {sell_signals} vs {buy_signals} (Quality: {quality_score}%)")
            else:
                self.logger.log(f"⚪ {strategy} No signal: BUY={buy_signals}, SELL={sell_signals} (Min: {min_threshold}, Quality: {quality_score}%)")
            
            return action, signals
            
        except Exception as e:
            self.logger.log(f"❌ Error in complete strategy analysis: {str(e)}")
            return None, [f"❌ Strategy error: {str(e)}"]
    
    def _generate_hft_signals(self, data: pd.DataFrame, buy_signals: int, sell_signals: int, 
                             signals: List[str], market_analysis: Dict[str, Any]) -> Tuple[int, int, List[str]]:
        """Generate HFT signals - Ultra-fast execution with micro movements."""
        try:
            last = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else last
            current_price = last['close']
            digits = 5
            
            # HFT Signal 1: EMA5 micro crossovers
            ema5 = last.get('EMA5', current_price)
            ema8 = last.get('EMA8', current_price)
            ema5_prev = prev.get('EMA5', current_price)
            ema8_prev = prev.get('EMA8', current_price)
            
            if ema5 > ema8 and ema5_prev <= ema8_prev:
                buy_signals += 4
                signals.append(f"⚡ HFT: EMA5>EMA8 cross @ {current_price:.{digits}f}")
            elif ema5 < ema8 and ema5_prev >= ema8_prev:
                sell_signals += 4
                signals.append(f"⚡ HFT: EMA5<EMA8 cross @ {current_price:.{digits}f}")
            
            # HFT Signal 2: RSI momentum (fast periods)
            rsi7 = last.get('RSI7', 50)
            rsi7_prev = prev.get('RSI7', 50)
            
            if rsi7 > 50 and rsi7_prev <= 50:
                buy_signals += 3
                signals.append(f"⚡ HFT: RSI7 bullish @ {rsi7:.1f}")
            elif rsi7 < 50 and rsi7_prev >= 50:
                sell_signals += 3
                signals.append(f"⚡ HFT: RSI7 bearish @ {rsi7:.1f}")
            
            # HFT Signal 3: Price action micro patterns
            price_change = abs(current_price - prev['close'])
            avg_change = data['close'].diff().abs().rolling(10).mean().iloc[-1]
            
            if price_change > avg_change * 2:  # Strong momentum
                if current_price > prev['close']:
                    buy_signals += 3
                    signals.append(f"⚡ HFT: Strong UP momentum")
                else:
                    sell_signals += 3
                    signals.append(f"⚡ HFT: Strong DOWN momentum")
            
            # HFT Signal 4: MACD histogram acceleration
            macd_hist = last.get('MACD_histogram', 0)
            macd_hist_prev = prev.get('MACD_histogram', 0)
            
            if macd_hist > 0 and macd_hist > macd_hist_prev:
                buy_signals += 2
                signals.append(f"⚡ HFT: MACD acceleration UP")
            elif macd_hist < 0 and macd_hist < macd_hist_prev:
                sell_signals += 2
                signals.append(f"⚡ HFT: MACD acceleration DOWN")
            
            return buy_signals, sell_signals, signals
            
        except Exception as e:
            self.logger.log(f"❌ Error in HFT signals: {str(e)}")
            return buy_signals, sell_signals, signals
    
    def _generate_scalping_signals(self, data: pd.DataFrame, buy_signals: int, sell_signals: int, 
                                  signals: List[str], market_analysis: Dict[str, Any]) -> Tuple[int, int, List[str]]:
        """Generate Scalping signals - Quick profits from small price movements."""
        try:
            last = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else last
            current_price = last['close']
            digits = 5
            
            # Scalping Signal 1: EMA5/EMA13 crossover with RSI confirmation
            ema5 = last.get('EMA5', current_price)
            ema13 = last.get('EMA13', current_price)
            rsi = last.get('RSI', 50)
            
            if last.get('EMA5_Cross_Above_EMA13', False):
                if 30 <= rsi <= 70:  # Not overbought/oversold
                    buy_signals += 5
                    signals.append(f"🎯 SCALP: EMA5>EMA13 + RSI @ {current_price:.{digits}f}")
                else:
                    buy_signals += 3
                    signals.append(f"🎯 SCALP: EMA5>EMA13 (RSI: {rsi:.1f})")
                    
            elif last.get('EMA5_Cross_Below_EMA13', False):
                if 30 <= rsi <= 70:
                    sell_signals += 5
                    signals.append(f"🎯 SCALP: EMA5<EMA13 + RSI @ {current_price:.{digits}f}")
                else:
                    sell_signals += 3
                    signals.append(f"🎯 SCALP: EMA5<EMA13 (RSI: {rsi:.1f})")
            
            # Scalping Signal 2: RSI oversold/overbought recovery
            if last.get('RSI_Oversold_Recovery', False):
                buy_signals += 4
                signals.append(f"🎯 SCALP: RSI oversold recovery @ {rsi:.1f}")
                
            elif last.get('RSI_Overbought_Decline', False):
                sell_signals += 4
                signals.append(f"🎯 SCALP: RSI overbought decline @ {rsi:.1f}")
            
            # Scalping Signal 3: Bollinger Band squeeze breakout
            bb_upper = last.get('BB_Upper', current_price)
            bb_lower = last.get('BB_Lower', current_price)
            bb_width = last.get('BB_Width', 0.02)
            
            if bb_width < 0.01:  # Tight squeeze
                if current_price > bb_upper and current_price > prev['close']:
                    buy_signals += 4
                    signals.append(f"🎯 SCALP: BB squeeze breakout UP @ {current_price:.{digits}f}")
                elif current_price < bb_lower and current_price < prev['close']:
                    sell_signals += 4
                    signals.append(f"🎯 SCALP: BB squeeze breakout DOWN @ {current_price:.{digits}f}")
            
            # Scalping Signal 4: Strong candle patterns
            if last.get('Strong_Bullish_Candle', False):
                buy_signals += 3
                signals.append(f"🎯 SCALP: Strong bullish candle")
                
            elif last.get('Strong_Bearish_Candle', False):
                sell_signals += 3
                signals.append(f"🎯 SCALP: Strong bearish candle")
            
            # Scalping Signal 5: Volume confirmation
            volume_surge = last.get('volume_surge', False)
            if volume_surge:
                if current_price > prev['close']:
                    buy_signals += 2
                    signals.append(f"🎯 SCALP: Volume surge UP")
                else:
                    sell_signals += 2
                    signals.append(f"🎯 SCALP: Volume surge DOWN")
            
            return buy_signals, sell_signals, signals
            
        except Exception as e:
            self.logger.log(f"❌ Error in Scalping signals: {str(e)}")
            return buy_signals, sell_signals, signals
    
    def _generate_intraday_signals(self, data: pd.DataFrame, buy_signals: int, sell_signals: int, 
                                  signals: List[str], market_analysis: Dict[str, Any]) -> Tuple[int, int, List[str]]:
        """Generate Intraday signals - Medium-term trend following."""
        try:
            last = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else last
            current_price = last['close']
            digits = 5
            
            # Intraday Signal 1: EMA20/EMA50 trend alignment
            ema20 = last.get('EMA20', current_price)
            ema50 = last.get('EMA50', current_price)
            ema200 = last.get('EMA200', current_price)
            
            if last.get('EMA20_Cross_Above_EMA50', False):
                if ema50 > ema200:  # Strong uptrend
                    buy_signals += 6
                    signals.append(f"📈 INTRADAY: Strong bullish trend @ {current_price:.{digits}f}")
                else:
                    buy_signals += 4
                    signals.append(f"📈 INTRADAY: EMA20>EMA50 cross @ {current_price:.{digits}f}")
                    
            elif last.get('EMA20_Cross_Below_EMA50', False):
                if ema50 < ema200:  # Strong downtrend
                    sell_signals += 6
                    signals.append(f"📉 INTRADAY: Strong bearish trend @ {current_price:.{digits}f}")
                else:
                    sell_signals += 4
                    signals.append(f"📉 INTRADAY: EMA20<EMA50 cross @ {current_price:.{digits}f}")
            
            # Intraday Signal 2: MACD trend confirmation
            macd = last.get('MACD', 0)
            macd_signal = last.get('MACD_signal', 0)
            macd_hist = last.get('MACD_histogram', 0)
            
            if macd > macd_signal and macd_hist > 0:
                buy_signals += 4
                signals.append(f"📈 INTRADAY: MACD bullish @ {current_price:.{digits}f}")
            elif macd < macd_signal and macd_hist < 0:
                sell_signals += 4
                signals.append(f"📉 INTRADAY: MACD bearish @ {current_price:.{digits}f}")
            
            # Intraday Signal 3: RSI trend support
            rsi = last.get('RSI', 50)
            if 40 <= rsi <= 60:  # Healthy trend range
                if ema20 > ema50:
                    buy_signals += 3
                    signals.append(f"📈 INTRADAY: Healthy bullish trend (RSI: {rsi:.1f})")
                elif ema20 < ema50:
                    sell_signals += 3
                    signals.append(f"📉 INTRADAY: Healthy bearish trend (RSI: {rsi:.1f})")
            
            # Intraday Signal 4: Breakout patterns
            if last.get('Bullish_Breakout', False):
                buy_signals += 5
                signals.append(f"📈 INTRADAY: Bullish breakout @ {current_price:.{digits}f}")
                
            elif last.get('Bearish_Breakout', False):
                sell_signals += 5
                signals.append(f"📉 INTRADAY: Bearish breakout @ {current_price:.{digits}f}")
            
            # Intraday Signal 5: ATR momentum
            atr = last.get('ATR', 0)
            atr_ratio = last.get('ATR_Ratio', 1)
            
            if atr_ratio > 1.2:  # High volatility
                if current_price > prev['close']:
                    buy_signals += 2
                    signals.append(f"📈 INTRADAY: High volatility UP")
                else:
                    sell_signals += 2
                    signals.append(f"📉 INTRADAY: High volatility DOWN")
            
            return buy_signals, sell_signals, signals
            
        except Exception as e:
            self.logger.log(f"❌ Error in Intraday signals: {str(e)}")
            return buy_signals, sell_signals, signals
    
    def _generate_arbitrage_signals(self, data: pd.DataFrame, buy_signals: int, sell_signals: int, 
                                   signals: List[str], market_analysis: Dict[str, Any]) -> Tuple[int, int, List[str]]:
        """Generate Arbitrage signals - Mean reversion and statistical opportunities."""
        try:
            last = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else last
            current_price = last['close']
            digits = 5
            
            # Arbitrage Signal 1: Bollinger Band mean reversion
            bb_upper = last.get('BB_Upper', current_price)
            bb_lower = last.get('BB_Lower', current_price)
            bb_middle = last.get('BB_Middle', current_price)
            
            if bb_upper != bb_lower:
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
                
                # Extreme oversold reversal
                if bb_position <= 0.05:  # Bottom 5%
                    rsi = last.get('RSI', 50)
                    if rsi < 25 and current_price > prev['close']:
                        buy_signals += 6
                        signals.append(f"⚖️ ARB: Extreme oversold reversal @ {current_price:.{digits}f}")
                    elif rsi < 35:
                        buy_signals += 4
                        signals.append(f"⚖️ ARB: Oversold bounce @ {current_price:.{digits}f}")
                
                # Extreme overbought reversal
                elif bb_position >= 0.95:  # Top 5%
                    rsi = last.get('RSI', 50)
                    if rsi > 75 and current_price < prev['close']:
                        sell_signals += 6
                        signals.append(f"⚖️ ARB: Extreme overbought reversal @ {current_price:.{digits}f}")
                    elif rsi > 65:
                        sell_signals += 4
                        signals.append(f"⚖️ ARB: Overbought decline @ {current_price:.{digits}f}")
            
            # Arbitrage Signal 2: Mean reversion from Bollinger middle
            if bb_middle > 0:
                distance_from_mean = abs(current_price - bb_middle) / bb_middle
                if distance_from_mean > 0.015:  # 1.5% deviation
                    if current_price < bb_middle and current_price > prev['close']:
                        buy_signals += 3
                        signals.append(f"⚖️ ARB: Below-mean recovery")
                    elif current_price > bb_middle and current_price < prev['close']:
                        sell_signals += 3
                        signals.append(f"⚖️ ARB: Above-mean decline")
            
            # Arbitrage Signal 3: RSI50 crossover with momentum
            rsi = last.get('RSI', 50)
            rsi_prev = prev.get('RSI', 50)
            ema20 = last.get('EMA20', current_price)
            macd_hist = last.get('MACD_histogram', 0)
            
            if rsi > 50 and rsi_prev <= 50:
                if current_price > ema20 and macd_hist > 0:
                    buy_signals += 3
                    signals.append(f"⚖️ ARB: RSI50 cross UP + momentum")
            elif rsi < 50 and rsi_prev >= 50:
                if current_price < ema20 and macd_hist < 0:
                    sell_signals += 3
                    signals.append(f"⚖️ ARB: RSI50 cross DOWN + momentum")
            
            # Arbitrage Signal 4: Support/Resistance bounce
            support_level = data['low'].rolling(20).min().iloc[-1]
            resistance_level = data['high'].rolling(20).max().iloc[-1]
            
            support_distance = abs(current_price - support_level) / current_price
            resistance_distance = abs(current_price - resistance_level) / current_price
            
            if support_distance < 0.002:  # Very close to support
                if current_price > prev['close'] and rsi < 40:
                    buy_signals += 4
                    signals.append(f"⚖️ ARB: Support bounce @ {support_level:.{digits}f}")
                    
            elif resistance_distance < 0.002:  # Very close to resistance
                if current_price < prev['close'] and rsi > 60:
                    sell_signals += 4
                    signals.append(f"⚖️ ARB: Resistance rejection @ {resistance_level:.{digits}f}")
            
            # Arbitrage Signal 5: Statistical reversion patterns
            price_std = data['close'].rolling(20).std().iloc[-1]
            price_mean = data['close'].rolling(20).mean().iloc[-1]
            
            if price_std > 0:
                z_score = (current_price - price_mean) / price_std
                if z_score < -2:  # 2 standard deviations below mean
                    buy_signals += 3
                    signals.append(f"⚖️ ARB: Statistical oversold (Z: {z_score:.2f})")
                elif z_score > 2:  # 2 standard deviations above mean
                    sell_signals += 3
                    signals.append(f"⚖️ ARB: Statistical overbought (Z: {z_score:.2f})")
            
            return buy_signals, sell_signals, signals
            
        except Exception as e:
            self.logger.log(f"❌ Error in Arbitrage signals: {str(e)}")
            return buy_signals, sell_signals, signals
    
    def _get_signal_threshold(self, strategy: str, quality_score: int) -> int:
        """Get minimum signal threshold based on strategy and quality."""
        base_thresholds = {
            "HFT": 2,       # Very aggressive
            "Scalping": 3,  # Moderate confirmation
            "Intraday": 4,  # Strong confirmation
            "Arbitrage": 2  # Quick mean reversion
        }
        
        base = base_thresholds.get(strategy, 3)
        
        # Adjust based on quality score
        if quality_score >= 80:
            return max(1, base - 1)  # Lower threshold for high quality
        elif quality_score >= 60:
            return base
        else:
            return base + 1  # Higher threshold for low quality