"""
Adaptive Risk Management Module
Dynamic risk adjustment based on market conditions and volatility
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time


class AdaptiveRiskManager:
    """Manages adaptive risk based on market volatility and conditions."""
    
    def __init__(self, logger, base_risk_manager):
        """Initialize adaptive risk manager."""
        self.logger = logger
        self.base_risk = base_risk_manager
        
        # Volatility tracking
        self.volatility_history = {}
        self.atr_history = {}
        self.spread_history = {}
        
        # Market regime detection
        self.market_regime = "NORMAL"  # NORMAL, HIGH_VOL, RANGING, TRENDING, NEWS_SPIKE
        self.regime_confidence = 0.5
        
        # Adaptive parameters
        self.vol_multipliers = {
            "LOW": 1.2,      # Increase position size in low volatility
            "NORMAL": 1.0,   # Standard position size
            "HIGH": 0.7,     # Reduce position size in high volatility
            "EXTREME": 0.3   # Minimal position size in extreme volatility
        }
        
        # Dynamic TP/SL multipliers based on regime
        self.tp_sl_multipliers = {
            "TRENDING": {"tp": 1.5, "sl": 0.8},    # Wider TP, tighter SL in trends
            "RANGING": {"tp": 0.8, "sl": 1.2},     # Tighter TP, wider SL in ranges
            "HIGH_VOL": {"tp": 1.2, "sl": 1.5},    # Both wider in high volatility
            "NEWS_SPIKE": {"tp": 0.5, "sl": 2.0}   # Very tight TP, wide SL during news
        }
        
        # Volatility thresholds (in ATR multiples)
        self.vol_thresholds = {
            "EXTREME": 3.0,
            "HIGH": 2.0,
            "NORMAL": 1.0,
            "LOW": 0.5
        }
        
        # Spread filtering
        self.max_spread_multipliers = {
            "EURUSD": 3.0,   # Max 3x normal spread
            "GBPUSD": 4.0,   # Max 4x normal spread
            "USDJPY": 3.5,   # Max 3.5x normal spread
            "XAUUSD": 5.0    # Max 5x normal spread (gold more volatile)
        }
        
        self.logger.log("✅ Adaptive Risk Manager initialized")
    
    def update_market_data(self, symbol: str, data: pd.DataFrame):
        """Update market data for volatility analysis."""
        try:
            if len(data) < 20:
                return
            
            # Calculate ATR for volatility measurement
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift(1))
            low_close = np.abs(data['low'] - data['close'].shift(1))
            
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr_14 = true_range.rolling(window=14).mean().iloc[-1]
            
            # Store ATR history
            if symbol not in self.atr_history:
                self.atr_history[symbol] = []
            
            self.atr_history[symbol].append({
                'timestamp': datetime.now(),
                'atr': atr_14,
                'close': data['close'].iloc[-1]
            })
            
            # Keep last 100 readings
            if len(self.atr_history[symbol]) > 100:
                self.atr_history[symbol] = self.atr_history[symbol][-100:]
            
            # Update volatility classification
            self._classify_volatility(symbol, atr_14)
            
            # Detect market regime
            self._detect_market_regime(symbol, data)
            
        except Exception as e:
            self.logger.log(f"❌ Error updating market data: {str(e)}")
    
    def update_spread_data(self, symbol: str, spread: float):
        """Update spread data for filtering."""
        if symbol not in self.spread_history:
            self.spread_history[symbol] = []
        
        self.spread_history[symbol].append({
            'timestamp': datetime.now(),
            'spread': spread
        })
        
        # Keep last 50 spread readings
        if len(self.spread_history[symbol]) > 50:
            self.spread_history[symbol] = self.spread_history[symbol][-50:]
    
    def _classify_volatility(self, symbol: str, current_atr: float):
        """Classify current volatility level."""
        if symbol not in self.atr_history or len(self.atr_history[symbol]) < 10:
            self.volatility_history[symbol] = "NORMAL"
            return
        
        # Calculate average ATR over last 20 periods
        recent_atrs = [h['atr'] for h in self.atr_history[symbol][-20:]]
        avg_atr = np.mean(recent_atrs)
        
        # Classify based on current vs average ATR
        ratio = current_atr / avg_atr if avg_atr > 0 else 1.0
        
        if ratio >= self.vol_thresholds["EXTREME"]:
            vol_class = "EXTREME"
        elif ratio >= self.vol_thresholds["HIGH"]:
            vol_class = "HIGH"
        elif ratio <= self.vol_thresholds["LOW"]:
            vol_class = "LOW"
        else:
            vol_class = "NORMAL"
        
        self.volatility_history[symbol] = vol_class
        
        # Log significant volatility changes
        if vol_class in ["EXTREME", "HIGH"]:
            self.logger.log(f"⚠️ {vol_class} volatility detected for {symbol}: ATR ratio {ratio:.2f}")
    
    def _detect_market_regime(self, symbol: str, data: pd.DataFrame):
        """Detect current market regime."""
        try:
            if len(data) < 50:
                return
            
            # Calculate trend strength
            ema_20 = data['close'].ewm(span=20).mean()
            ema_50 = data['close'].ewm(span=50).mean()
            
            # Trend strength based on EMA separation
            trend_strength = abs(ema_20.iloc[-1] - ema_50.iloc[-1]) / ema_50.iloc[-1]
            
            # Range detection
            recent_high = data['high'].tail(20).max()
            recent_low = data['low'].tail(20).min()
            range_size = (recent_high - recent_low) / data['close'].iloc[-1]
            
            # Volatility spike detection
            current_vol = self.volatility_history.get(symbol, "NORMAL")
            
            # Determine regime
            if current_vol == "EXTREME":
                self.market_regime = "NEWS_SPIKE"
                self.regime_confidence = 0.9
            elif current_vol == "HIGH":
                self.market_regime = "HIGH_VOL"
                self.regime_confidence = 0.8
            elif trend_strength > 0.02:  # 2% EMA separation
                self.market_regime = "TRENDING"
                self.regime_confidence = trend_strength * 20  # Convert to confidence
            elif range_size < 0.01:  # 1% range
                self.market_regime = "RANGING"
                self.regime_confidence = 0.7
            else:
                self.market_regime = "NORMAL"
                self.regime_confidence = 0.6
            
            # Ensure confidence is between 0 and 1
            self.regime_confidence = min(1.0, max(0.1, self.regime_confidence))
            
        except Exception as e:
            self.logger.log(f"❌ Error detecting market regime: {str(e)}")
    
    def get_adaptive_lot_size(self, symbol: str, base_lot: float) -> float:
        """Calculate adaptive lot size based on volatility."""
        try:
            vol_class = self.volatility_history.get(symbol, "NORMAL")
            multiplier = self.vol_multipliers.get(vol_class, 1.0)
            
            adaptive_lot = base_lot * multiplier
            
            # Ensure lot size is within reasonable bounds
            min_lot = 0.01
            max_lot = base_lot * 2.0  # Never more than 2x base
            
            adaptive_lot = max(min_lot, min(max_lot, adaptive_lot))
            
            if multiplier != 1.0:
                self.logger.log(f"📊 Adaptive lot for {symbol}: {base_lot} → {adaptive_lot:.2f} ({vol_class})")
            
            return adaptive_lot
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating adaptive lot: {str(e)}")
            return base_lot
    
    def get_dynamic_tp_sl(self, symbol: str, base_tp: float, base_sl: float) -> Tuple[float, float]:
        """Calculate dynamic TP/SL based on market regime."""
        try:
            regime_multipliers = self.tp_sl_multipliers.get(self.market_regime, {"tp": 1.0, "sl": 1.0})
            
            dynamic_tp = base_tp * regime_multipliers["tp"]
            dynamic_sl = base_sl * regime_multipliers["sl"]
            
            # Ensure TP/SL are reasonable
            dynamic_tp = max(base_tp * 0.5, min(base_tp * 2.0, dynamic_tp))
            dynamic_sl = max(base_sl * 0.5, min(base_sl * 3.0, dynamic_sl))
            
            if regime_multipliers["tp"] != 1.0 or regime_multipliers["sl"] != 1.0:
                self.logger.log(f"📊 Dynamic TP/SL for {symbol}: TP {base_tp} → {dynamic_tp:.1f}, SL {base_sl} → {dynamic_sl:.1f} ({self.market_regime})")
            
            return dynamic_tp, dynamic_sl
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating dynamic TP/SL: {str(e)}")
            return base_tp, base_sl
    
    def should_filter_signal(self, symbol: str, current_spread: float) -> Tuple[bool, str]:
        """Determine if signal should be filtered based on spread."""
        try:
            # Get normal spread for symbol
            if symbol not in self.spread_history or len(self.spread_history[symbol]) < 5:
                return False, "Insufficient spread data"
            
            recent_spreads = [s['spread'] for s in self.spread_history[symbol][-10:]]
            normal_spread = np.median(recent_spreads)
            
            max_allowed = normal_spread * self.max_spread_multipliers.get(symbol, 3.0)
            
            if current_spread > max_allowed:
                return True, f"Spread too wide: {current_spread:.1f} > {max_allowed:.1f}"
            
            return False, "Spread acceptable"
            
        except Exception as e:
            self.logger.log(f"❌ Error checking spread filter: {str(e)}")
            return False, f"Filter error: {str(e)}"
    
    def should_pause_trading(self, symbol: str) -> Tuple[bool, str]:
        """Determine if trading should be paused."""
        try:
            vol_class = self.volatility_history.get(symbol, "NORMAL")
            
            # Pause during extreme volatility
            if vol_class == "EXTREME":
                return True, f"Extreme volatility detected ({vol_class})"
            
            # Check for news spikes
            if self.market_regime == "NEWS_SPIKE" and self.regime_confidence > 0.8:
                return True, f"News spike detected (confidence: {self.regime_confidence:.1f})"
            
            return False, "Trading conditions normal"
            
        except Exception as e:
            self.logger.log(f"❌ Error checking trading pause: {str(e)}")
            return False, f"Check error: {str(e)}"
    
    def get_risk_summary(self, symbol: str) -> Dict:
        """Get comprehensive risk summary."""
        vol_class = self.volatility_history.get(symbol, "NORMAL")
        
        return {
            'symbol': symbol,
            'volatility_class': vol_class,
            'market_regime': self.market_regime,
            'regime_confidence': f"{self.regime_confidence:.2f}",
            'lot_multiplier': self.vol_multipliers.get(vol_class, 1.0),
            'tp_multiplier': self.tp_sl_multipliers.get(self.market_regime, {}).get("tp", 1.0),
            'sl_multiplier': self.tp_sl_multipliers.get(self.market_regime, {}).get("sl", 1.0),
            'atr_readings': len(self.atr_history.get(symbol, [])),
            'spread_readings': len(self.spread_history.get(symbol, []))
        }


class VolatilityFilter:
    """Advanced volatility filtering for signal quality."""
    
    def __init__(self, logger):
        """Initialize volatility filter."""
        self.logger = logger
        self.volatility_cache = {}
        self.session_volatility = {}
        
        # Session-specific volatility multipliers
        self.session_multipliers = {
            'asia': 0.7,      # Lower volatility in Asian session
            'london': 1.2,    # Higher volatility in London session
            'new_york': 1.0,  # Normal volatility in NY session
            'overlap': 1.5    # Highest volatility during overlaps
        }
        
        self.logger.log("✅ Volatility Filter initialized")
    
    def calculate_volatility_score(self, data: pd.DataFrame, symbol: str) -> float:
        """Calculate volatility score for signal filtering."""
        try:
            if len(data) < 20:
                return 0.5  # Neutral score
            
            # Calculate multiple volatility measures
            returns = data['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(len(returns))
            
            # ATR-based volatility
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift(1))
            low_close = np.abs(data['low'] - data['close'].shift(1))
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(window=14).mean().iloc[-1]
            atr_normalized = atr / data['close'].iloc[-1]
            
            # Combine volatility measures
            vol_score = (volatility * 0.6 + atr_normalized * 0.4)
            
            # Normalize to 0-1 scale
            vol_score = min(1.0, max(0.0, vol_score * 100))
            
            self.volatility_cache[symbol] = vol_score
            return vol_score
            
        except Exception as e:
            self.logger.log(f"❌ Error calculating volatility score: {str(e)}")
            return 0.5
    
    def adjust_quality_threshold(self, base_threshold: int, vol_score: float, session: str) -> int:
        """Adjust quality threshold based on volatility and session."""
        try:
            # Session adjustment
            session_mult = self.session_multipliers.get(session, 1.0)
            
            # Volatility adjustment (higher volatility = higher threshold)
            vol_adjustment = 1.0 + (vol_score * 0.5)  # Up to 50% increase
            
            # Combined adjustment
            adjusted_threshold = base_threshold * session_mult * vol_adjustment
            
            return int(min(20, max(2, adjusted_threshold)))  # Ensure reasonable bounds
            
        except Exception as e:
            self.logger.log(f"❌ Error adjusting quality threshold: {str(e)}")
            return base_threshold
    
    def filter_noise_signals(self, signals: List[str], vol_score: float) -> List[str]:
        """Filter out noise signals during high volatility."""
        try:
            if vol_score < 0.7:  # Normal volatility
                return signals
            
            # In high volatility, filter out weak signals
            filtered_signals = []
            
            for signal in signals:
                # Keep strong signals
                if any(keyword in signal.lower() for keyword in [
                    'strong', 'breakout', 'momentum', 'volume', 'confluence'
                ]):
                    filtered_signals.append(signal)
                # Filter out weak signals
                elif any(keyword in signal.lower() for keyword in [
                    'weak', 'minor', 'small', 'slight'
                ]):
                    continue
                else:
                    # Keep neutral signals
                    filtered_signals.append(signal)
            
            if len(filtered_signals) < len(signals):
                self.logger.log(f"🔍 Filtered {len(signals) - len(filtered_signals)} noise signals (vol: {vol_score:.2f})")
            
            return filtered_signals
            
        except Exception as e:
            self.logger.log(f"❌ Error filtering noise signals: {str(e)}")
            return signals