"""
AI-Enhanced Market Analysis Module
Implements advanced market structure analysis and signal quality scoring
Based on bobot2.py lines 3194-3221 and 3099-3192
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import time


class AIMarketAnalyzer:
    """AI-powered market structure analysis and signal quality scoring."""
    
    def __init__(self, logger):
        """Initialize AI analyzer."""
        self.logger = logger
        self.analysis_cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
    def analyze_market_structure(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """
        AI-enhanced market structure analysis from bobot2.py.
        
        Args:
            data: OHLCV DataFrame with indicators
            symbol: Trading symbol
            
        Returns:
            Dict with market structure analysis
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_structure_{int(time.time() // self.cache_duration)}"
            if cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key]
            
            if len(data) < 50:
                return {"market_structure": "NEUTRAL", "confidence": 0, "trend_strength": 0}
            
            last = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else last
            
            # AI Analysis Factors
            analysis = {
                "market_structure": "NEUTRAL",
                "confidence": 0,
                "trend_strength": 0,
                "volatility_state": "NORMAL",
                "momentum_direction": "NEUTRAL",
                "support_resistance": {},
                "quality_factors": []
            }
            
            # 1. EMA Alignment Analysis (25 points)
            ema5 = last.get('EMA5', last['close'])
            ema13 = last.get('EMA13', last['close'])
            ema50 = last.get('EMA50', last['close'])
            ema200 = last.get('EMA200', last['close'])
            
            if ema5 > ema13 > ema50 > ema200:
                analysis["market_structure"] = "BULLISH"
                analysis["confidence"] += 25
                analysis["trend_strength"] += 30
                analysis["quality_factors"].append("Strong bullish EMA alignment")
            elif ema5 < ema13 < ema50 < ema200:
                analysis["market_structure"] = "BEARISH"
                analysis["confidence"] += 25
                analysis["trend_strength"] += 30
                analysis["quality_factors"].append("Strong bearish EMA alignment")
            elif ema5 > ema13 > ema50:
                analysis["market_structure"] = "BULLISH" if analysis["market_structure"] == "NEUTRAL" else analysis["market_structure"]
                analysis["confidence"] += 15
                analysis["trend_strength"] += 20
                analysis["quality_factors"].append("Medium bullish alignment")
            elif ema5 < ema13 < ema50:
                analysis["market_structure"] = "BEARISH" if analysis["market_structure"] == "NEUTRAL" else analysis["market_structure"]
                analysis["confidence"] += 15
                analysis["trend_strength"] += 20
                analysis["quality_factors"].append("Medium bearish alignment")
            
            # 2. Price Action Momentum (20 points)
            price_change = (last['close'] - prev['close']) / prev['close'] * 100
            if abs(price_change) > 0.1:  # Significant movement
                if price_change > 0:
                    analysis["momentum_direction"] = "BULLISH"
                    analysis["confidence"] += 20
                    analysis["quality_factors"].append(f"Strong bullish momentum (+{price_change:.2f}%)")
                else:
                    analysis["momentum_direction"] = "BEARISH"
                    analysis["confidence"] += 20
                    analysis["quality_factors"].append(f"Strong bearish momentum ({price_change:.2f}%)")
            
            # 3. RSI Confluence Analysis (15 points)
            rsi = last.get('RSI', 50)
            if 40 <= rsi <= 60:
                analysis["confidence"] += 15
                analysis["quality_factors"].append("RSI in optimal range")
            elif 30 <= rsi <= 70:
                analysis["confidence"] += 10
                analysis["quality_factors"].append("RSI in good range")
            elif rsi < 25 or rsi > 75:
                analysis["confidence"] += 8
                analysis["quality_factors"].append("RSI extreme - reversal potential")
            
            # 4. MACD Momentum Analysis (15 points)
            macd_hist = last.get('MACD_histogram', 0)
            macd_hist_prev = prev.get('MACD_histogram', 0)
            if abs(macd_hist) > abs(macd_hist_prev):
                analysis["confidence"] += 15
                analysis["quality_factors"].append("MACD momentum increasing")
                if macd_hist > 0:
                    analysis["momentum_direction"] = "BULLISH"
                else:
                    analysis["momentum_direction"] = "BEARISH"
            
            # 5. Bollinger Band Position Analysis (15 points)
            bb_upper = last.get('BB_Upper', last['close'])
            bb_lower = last.get('BB_Lower', last['close'])
            bb_middle = last.get('BB_Middle', last['close'])
            
            if bb_upper != bb_lower:  # Valid BB data
                bb_position = (last['close'] - bb_lower) / (bb_upper - bb_lower)
                if bb_position > 0.8:
                    analysis["confidence"] += 10
                    analysis["quality_factors"].append("Near BB upper - overbought")
                    analysis["volatility_state"] = "HIGH"
                elif bb_position < 0.2:
                    analysis["confidence"] += 10
                    analysis["quality_factors"].append("Near BB lower - oversold")
                    analysis["volatility_state"] = "HIGH"
                elif 0.4 <= bb_position <= 0.6:
                    analysis["confidence"] += 15
                    analysis["quality_factors"].append("Price near BB middle - balanced")
            
            # 6. Volume Analysis (10 points) - if available
            if 'volume' in data.columns:
                vol_avg = data['volume'].rolling(20).mean().iloc[-1]
                current_vol = last.get('volume', 1)
                if current_vol > vol_avg * 1.5:
                    analysis["confidence"] += 10
                    analysis["quality_factors"].append("High volume confirmation")
                elif current_vol > vol_avg * 1.2:
                    analysis["confidence"] += 5
                    analysis["quality_factors"].append("Above average volume")
            
            # 7. Support/Resistance Levels
            support_level = data['low'].rolling(20).min().iloc[-1]
            resistance_level = data['high'].rolling(20).max().iloc[-1]
            
            support_distance = abs(last['close'] - support_level) / last['close']
            resistance_distance = abs(last['close'] - resistance_level) / last['close']
            
            analysis["support_resistance"] = {
                "support": support_level,
                "resistance": resistance_level,
                "support_distance": support_distance,
                "resistance_distance": resistance_distance,
                "near_support": support_distance < 0.002,
                "near_resistance": resistance_distance < 0.002
            }
            
            # Adjust confidence based on market structure consistency
            if analysis["market_structure"] == analysis["momentum_direction"]:
                analysis["confidence"] += 10
                analysis["quality_factors"].append("Market structure and momentum aligned")
            
            # Cache the analysis
            self.analysis_cache[cache_key] = analysis
            
            self.logger.log(f"🤖 AI Market Analysis for {symbol}:")
            self.logger.log(f"   Structure: {analysis['market_structure']} (Confidence: {analysis['confidence']}%)")
            self.logger.log(f"   Trend Strength: {analysis['trend_strength']}%")
            self.logger.log(f"   Quality Factors: {len(analysis['quality_factors'])}")
            
            return analysis
            
        except Exception as e:
            self.logger.log(f"❌ Error in AI market analysis: {str(e)}")
            return {"market_structure": "NEUTRAL", "confidence": 0, "trend_strength": 0}
    
    def calculate_signal_quality_score(self, data: pd.DataFrame, signals: List[str], 
                                     market_analysis: Dict[str, Any]) -> int:
        """
        Calculate signal quality score from bobot2.py (lines 3099-3192).
        
        Args:
            data: OHLCV DataFrame with indicators
            signals: List of generated signals
            market_analysis: AI market analysis results
            
        Returns:
            int: Quality score (0-100)
        """
        try:
            if len(data) < 10:
                return 0
            
            last = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else last
            
            quality_score = 0
            quality_factors = []
            
            # Factor 1: Market Structure Alignment (25 points)
            market_confidence = market_analysis.get("confidence", 0)
            if market_confidence >= 70:
                quality_score += 25
                quality_factors.append("High market structure confidence")
            elif market_confidence >= 50:
                quality_score += 15
                quality_factors.append("Medium market structure confidence")
            elif market_confidence >= 30:
                quality_score += 10
                quality_factors.append("Low market structure confidence")
            
            # Factor 2: Trend Strength (20 points)
            trend_strength = market_analysis.get("trend_strength", 0)
            if trend_strength >= 25:
                quality_score += 20
                quality_factors.append("Strong trend detected")
            elif trend_strength >= 15:
                quality_score += 15
                quality_factors.append("Medium trend strength")
            elif trend_strength >= 5:
                quality_score += 10
                quality_factors.append("Weak trend present")
            
            # Factor 3: Signal Confluence (20 points)
            signal_count = len(signals)
            if signal_count >= 5:
                quality_score += 20
                quality_factors.append("High signal confluence")
            elif signal_count >= 3:
                quality_score += 15
                quality_factors.append("Medium signal confluence")
            elif signal_count >= 2:
                quality_score += 10
                quality_factors.append("Basic signal confluence")
            
            # Factor 4: RSI Positioning (15 points)
            rsi = last.get('RSI', 50)
            if 40 <= rsi <= 60:
                quality_score += 15
                quality_factors.append("RSI in optimal zone")
            elif 30 <= rsi <= 70:
                quality_score += 10
                quality_factors.append("RSI in acceptable zone")
            elif rsi < 25 or rsi > 75:
                quality_score += 8
                quality_factors.append("RSI extreme level")
            
            # Factor 5: Price Action Quality (10 points)
            volatility_state = market_analysis.get("volatility_state", "NORMAL")
            if volatility_state == "HIGH":
                quality_score += 10
                quality_factors.append("High volatility environment")
            elif volatility_state == "NORMAL":
                quality_score += 5
                quality_factors.append("Normal volatility")
            
            # Factor 6: Support/Resistance Context (10 points)
            sr_data = market_analysis.get("support_resistance", {})
            if sr_data.get("near_support") or sr_data.get("near_resistance"):
                quality_score += 10
                quality_factors.append("Near key support/resistance level")
            elif sr_data.get("support_distance", 1) < 0.01 or sr_data.get("resistance_distance", 1) < 0.01:
                quality_score += 5
                quality_factors.append("Within support/resistance zone")
            
            self.logger.log(f"📊 Signal Quality Score: {quality_score}/100")
            for factor in quality_factors:
                self.logger.log(f"   ✓ {factor}")
            
            return min(100, quality_score)
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating signal quality: {str(e)}")
            return 0
    
    def enhance_signals_with_ai(self, data: pd.DataFrame, initial_signals: List[str],
                              market_analysis: Dict[str, Any], strategy: str) -> Tuple[List[str], int, int]:
        """
        Enhance signals using AI analysis from bobot2.py (lines 3194-3221).
        
        Args:
            data: OHLCV DataFrame
            initial_signals: Initial signal list
            market_analysis: AI market analysis
            strategy: Current strategy name
            
        Returns:
            Tuple of (enhanced_signals, buy_signals, sell_signals)
        """
        try:
            if len(data) < 10:
                return initial_signals, 0, 0
            
            enhanced_signals = initial_signals.copy()
            buy_signals = 0
            sell_signals = 0
            
            last = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else last
            
            current_price = last['close']
            digits = 5  # Default for forex
            
            # AI-Enhanced Signal Generation
            market_structure = market_analysis.get("market_structure", "NEUTRAL")
            confidence = market_analysis.get("confidence", 0)
            momentum = market_analysis.get("momentum_direction", "NEUTRAL")
            
            # 1. AI-Aligned Signal Enhancement
            if market_structure == "BULLISH" and confidence > 50:
                rsi = last.get('RSI', 50)
                ema5 = last.get('EMA5', current_price)
                ema13 = last.get('EMA13', current_price)
                
                # Focus on BUY signals in bullish market
                if rsi < 40:  # Oversold in bullish market = opportunity
                    buy_signals += 3
                    enhanced_signals.append(f"🤖 AI-BULLISH: RSI dip buy @ {current_price:.{digits}f} (RSI: {rsi:.1f})")
                elif ema5 > ema13:
                    buy_signals += 2
                    enhanced_signals.append(f"🤖 AI-BULLISH: EMA alignment buy @ {current_price:.{digits}f}")
                    
            elif market_structure == "BEARISH" and confidence > 50:
                rsi = last.get('RSI', 50)
                ema5 = last.get('EMA5', current_price)
                ema13 = last.get('EMA13', current_price)
                
                # Focus on SELL signals in bearish market
                if rsi > 60:  # Overbought in bearish market = opportunity
                    sell_signals += 3
                    enhanced_signals.append(f"🤖 AI-BEARISH: RSI peak sell @ {current_price:.{digits}f} (RSI: {rsi:.1f})")
                elif ema5 < ema13:
                    sell_signals += 2
                    enhanced_signals.append(f"🤖 AI-BEARISH: EMA alignment sell @ {current_price:.{digits}f}")
            
            # 2. Momentum-Based Signals
            if momentum == "BULLISH" and confidence > 30:
                price_change_pips = abs(current_price - prev['close']) * 10000  # Convert to pips
                if price_change_pips > 5:  # Significant movement
                    buy_signals += 2
                    enhanced_signals.append(f"🎯 MOMENTUM: Strong UP {price_change_pips:.1f} pips @ {current_price:.{digits}f}")
                    
            elif momentum == "BEARISH" and confidence > 30:
                price_change_pips = abs(current_price - prev['close']) * 10000
                if price_change_pips > 5:
                    sell_signals += 2
                    enhanced_signals.append(f"🎯 MOMENTUM: Strong DOWN {price_change_pips:.1f} pips @ {current_price:.{digits}f}")
            
            # 3. Support/Resistance AI Signals
            sr_data = market_analysis.get("support_resistance", {})
            if sr_data:
                if sr_data.get("near_support") and momentum != "BEARISH":
                    rsi = last.get('RSI', 50)
                    if rsi < 40 and current_price > prev['close']:
                        buy_signals += 3
                        enhanced_signals.append(f"🤖 AI: Support bounce + oversold @ {current_price:.{digits}f}")
                        
                elif sr_data.get("near_resistance") and momentum != "BULLISH":
                    rsi = last.get('RSI', 50)
                    if rsi > 60 and current_price < prev['close']:
                        sell_signals += 3
                        enhanced_signals.append(f"🤖 AI: Resistance rejection + overbought @ {current_price:.{digits}f}")
            
            # 4. Quality-Based Signal Boost
            if confidence >= 70:
                # High confidence market structure gets signal boost
                if market_structure == "BULLISH":
                    buy_signals += 2
                    enhanced_signals.append(f"🌟 HIGH-CONFIDENCE: Strong bullish structure @ {current_price:.{digits}f}")
                elif market_structure == "BEARISH":
                    sell_signals += 2
                    enhanced_signals.append(f"🌟 HIGH-CONFIDENCE: Strong bearish structure @ {current_price:.{digits}f}")
            
            return enhanced_signals, buy_signals, sell_signals
            
        except Exception as e:
            self.logger.log(f"❌ Error enhancing signals with AI: {str(e)}")
            return initial_signals, 0, 0