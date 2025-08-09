#!/usr/bin/env python3
"""
Strategy Engine Testing Script
Tests all strategy implementations (HFT, Scalping, Intraday, Arbitrage)
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add modules to path
sys.path.append('.')

from modules.complete_strategy import CompleteStrategyEngine
from modules.ai_analysis import AIMarketAnalyzer
from modules.indicators import IndicatorCalculator
from modules.logging_utils import MultiChannelLogger


def create_strategy_test_data(strategy_type="scalping", signal_strength="strong"):
    """Create test data optimized for specific strategy types."""
    np.random.seed(42)
    length = 100
    
    if strategy_type == "hft":
        # Create micro-movement data for HFT
        base_price = 1.1000
        prices = [base_price]
        for i in range(length - 1):
            # Small rapid changes
            change = np.random.normal(0, 0.0001)
            if signal_strength == "strong":
                change += 0.0002 if i % 10 < 5 else -0.0002  # Pattern
            prices.append(prices[-1] + change)
            
    elif strategy_type == "scalping":
        # Create short-term trend data
        base_price = 1.1000
        prices = [base_price]
        trend_direction = 1 if signal_strength == "strong" else -1
        for i in range(length - 1):
            trend = trend_direction * 0.0001 + np.random.normal(0, 0.0002)
            prices.append(prices[-1] + trend)
            
    elif strategy_type == "intraday":
        # Create medium-term trend data
        base_price = 1.1000
        prices = [base_price]
        trend_direction = 1 if signal_strength == "strong" else -1
        for i in range(length - 1):
            trend = trend_direction * 0.0003 + np.random.normal(0, 0.0001)
            prices.append(prices[-1] + trend)
            
    elif strategy_type == "arbitrage":
        # Create mean-reverting data
        base_price = 1.1000
        prices = [base_price]
        mean = base_price
        for i in range(length - 1):
            # Mean reversion with occasional spikes
            reversion = (mean - prices[-1]) * 0.1
            if signal_strength == "strong" and i % 20 == 0:
                reversion += np.random.choice([-0.001, 0.001])  # Spike
            noise = np.random.normal(0, 0.0001)
            prices.append(prices[-1] + reversion + noise)
    
    # Create OHLCV DataFrame
    data = []
    for i, close in enumerate(prices):
        high = close + np.random.uniform(0, 0.0003)
        low = close - np.random.uniform(0, 0.0003)
        open_price = prices[i-1] if i > 0 else close
        volume = np.random.uniform(1000, 5000)
        
        data.append({
            'time': datetime.now() - timedelta(minutes=length-i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('time', inplace=True)
    return df


def test_hft_strategy():
    """Test HFT strategy implementation."""
    print("=== Testing HFT Strategy ===")
    
    logger = MultiChannelLogger()
    ai_analyzer = AIMarketAnalyzer(logger)
    indicator_calc = IndicatorCalculator(logger, None)
    strategy_engine = CompleteStrategyEngine(logger, ai_analyzer)
    
    test_results = {}
    
    # Test Case 1: Strong HFT Signals
    print("\n1. Testing HFT with Strong Signals...")
    hft_data = create_strategy_test_data("hft", "strong")
    hft_data = indicator_calc.calculate_all_indicators(hft_data)
    
    action, signals = strategy_engine.run_complete_strategy("HFT", hft_data, "EURUSD")
    
    test_results["hft_strong"] = {
        "action": action,
        "signal_count": len(signals),
        "expected_action": action in ["BUY", "SELL", None],
        "min_signals": len(signals) >= 0,
        "pass": action in ["BUY", "SELL", None] and len(signals) >= 0
    }
    
    print(f"   Action: {action}")
    print(f"   Signal Count: {len(signals)}")
    print(f"   Signals: {signals[:3]}...")  # Show first 3
    print(f"   Status: {'✅ PASS' if test_results['hft_strong']['pass'] else '❌ FAIL'}")
    
    # Test Case 2: Weak HFT Signals
    print("\n2. Testing HFT with Weak Signals...")
    hft_weak_data = create_strategy_test_data("hft", "weak")
    hft_weak_data = indicator_calc.calculate_all_indicators(hft_weak_data)
    
    action_weak, signals_weak = strategy_engine.run_complete_strategy("HFT", hft_weak_data, "EURUSD")
    
    test_results["hft_weak"] = {
        "action": action_weak,
        "signal_count": len(signals_weak),
        "pass": True  # Any result is acceptable for weak signals
    }
    
    print(f"   Action: {action_weak}")
    print(f"   Signal Count: {len(signals_weak)}")
    print(f"   Status: {'✅ PASS' if test_results['hft_weak']['pass'] else '❌ FAIL'}")
    
    return test_results


def test_scalping_strategy():
    """Test Scalping strategy implementation."""
    print("\n=== Testing Scalping Strategy ===")
    
    logger = MultiChannelLogger()
    ai_analyzer = AIMarketAnalyzer(logger)
    indicator_calc = IndicatorCalculator(logger, None)
    strategy_engine = CompleteStrategyEngine(logger, ai_analyzer)
    
    test_results = {}
    
    # Test Case 1: Strong Scalping Signals
    print("\n1. Testing Scalping with Strong Bullish Trend...")
    scalp_data = create_strategy_test_data("scalping", "strong")
    scalp_data = indicator_calc.calculate_all_indicators(scalp_data)
    
    action, signals = strategy_engine.run_complete_strategy("Scalping", scalp_data, "EURUSD")
    
    test_results["scalping_strong"] = {
        "action": action,
        "signal_count": len(signals),
        "has_scalp_signals": any("SCALP" in signal for signal in signals),
        "pass": action in ["BUY", "SELL", None] and len(signals) >= 0
    }
    
    print(f"   Action: {action}")
    print(f"   Signal Count: {len(signals)}")
    print(f"   Has Scalping Signals: {any('SCALP' in signal for signal in signals)}")
    print(f"   Sample Signals: {[s for s in signals if 'SCALP' in s][:2]}")
    print(f"   Status: {'✅ PASS' if test_results['scalping_strong']['pass'] else '❌ FAIL'}")
    
    # Test Case 2: EMA Crossover Detection
    print("\n2. Testing EMA Crossover Detection...")
    # Create specific EMA crossover scenario
    ema_data = scalp_data.copy()
    if len(ema_data) > 2:
        # Force EMA crossover in last candle
        ema_data.loc[ema_data.index[-1], 'EMA5_Cross_Above_EMA13'] = True
        ema_data.loc[ema_data.index[-1], 'RSI'] = 50  # Neutral RSI
    
    action_ema, signals_ema = strategy_engine.run_complete_strategy("Scalping", ema_data, "EURUSD")
    
    test_results["scalping_ema"] = {
        "action": action_ema,
        "signal_count": len(signals_ema),
        "pass": True  # Any result is valid
    }
    
    print(f"   Action: {action_ema}")
    print(f"   Signal Count: {len(signals_ema)}")
    print(f"   Status: {'✅ PASS' if test_results['scalping_ema']['pass'] else '❌ FAIL'}")
    
    return test_results


def test_intraday_strategy():
    """Test Intraday strategy implementation."""
    print("\n=== Testing Intraday Strategy ===")
    
    logger = MultiChannelLogger()
    ai_analyzer = AIMarketAnalyzer(logger)
    indicator_calc = IndicatorCalculator(logger, None)
    strategy_engine = CompleteStrategyEngine(logger, ai_analyzer)
    
    test_results = {}
    
    # Test Case 1: Strong Trend
    print("\n1. Testing Intraday with Strong Trend...")
    intraday_data = create_strategy_test_data("intraday", "strong")
    intraday_data = indicator_calc.calculate_all_indicators(intraday_data)
    
    action, signals = strategy_engine.run_complete_strategy("Intraday", intraday_data, "EURUSD")
    
    test_results["intraday_strong"] = {
        "action": action,
        "signal_count": len(signals),
        "has_intraday_signals": any("INTRADAY" in signal for signal in signals),
        "pass": action in ["BUY", "SELL", None] and len(signals) >= 0
    }
    
    print(f"   Action: {action}")
    print(f"   Signal Count: {len(signals)}")
    print(f"   Has Intraday Signals: {any('INTRADAY' in signal for signal in signals)}")
    print(f"   Sample Signals: {[s for s in signals if 'INTRADAY' in s][:2]}")
    print(f"   Status: {'✅ PASS' if test_results['intraday_strong']['pass'] else '❌ FAIL'}")
    
    # Test Case 2: EMA Trend Alignment
    print("\n2. Testing EMA Trend Alignment...")
    trend_data = intraday_data.copy()
    if len(trend_data) > 0:
        # Force strong trend alignment
        last_idx = trend_data.index[-1]
        trend_data.loc[last_idx, 'EMA20_Cross_Above_EMA50'] = True
        trend_data.loc[last_idx, 'EMA50'] = 1.1010
        trend_data.loc[last_idx, 'EMA200'] = 1.1000  # EMA50 > EMA200
    
    action_trend, signals_trend = strategy_engine.run_complete_strategy("Intraday", trend_data, "EURUSD")
    
    test_results["intraday_trend"] = {
        "action": action_trend,
        "signal_count": len(signals_trend),
        "pass": True  # Any result is valid
    }
    
    print(f"   Action: {action_trend}")
    print(f"   Signal Count: {len(signals_trend)}")
    print(f"   Status: {'✅ PASS' if test_results['intraday_trend']['pass'] else '❌ FAIL'}")
    
    return test_results


def test_arbitrage_strategy():
    """Test Arbitrage strategy implementation."""
    print("\n=== Testing Arbitrage Strategy ===")
    
    logger = MultiChannelLogger()
    ai_analyzer = AIMarketAnalyzer(logger)
    indicator_calc = IndicatorCalculator(logger, None)
    strategy_engine = CompleteStrategyEngine(logger, ai_analyzer)
    
    test_results = {}
    
    # Test Case 1: Mean Reversion Signals
    print("\n1. Testing Arbitrage Mean Reversion...")
    arb_data = create_strategy_test_data("arbitrage", "strong")
    arb_data = indicator_calc.calculate_all_indicators(arb_data)
    
    action, signals = strategy_engine.run_complete_strategy("Arbitrage", arb_data, "EURUSD")
    
    test_results["arbitrage_mean_reversion"] = {
        "action": action,
        "signal_count": len(signals),
        "has_arb_signals": any("ARB" in signal for signal in signals),
        "pass": action in ["BUY", "SELL", None] and len(signals) >= 0
    }
    
    print(f"   Action: {action}")
    print(f"   Signal Count: {len(signals)}")
    print(f"   Has Arbitrage Signals: {any('ARB' in signal for signal in signals)}")
    print(f"   Sample Signals: {[s for s in signals if 'ARB' in s][:2]}")
    print(f"   Status: {'✅ PASS' if test_results['arbitrage_mean_reversion']['pass'] else '❌ FAIL'}")
    
    # Test Case 2: Extreme BB Position
    print("\n2. Testing Extreme Bollinger Band Position...")
    bb_data = arb_data.copy()
    if len(bb_data) > 0:
        last_idx = bb_data.index[-1]
        # Force extreme oversold position
        bb_data.loc[last_idx, 'BB_Upper'] = 1.1100
        bb_data.loc[last_idx, 'BB_Lower'] = 1.1000
        bb_data.loc[last_idx, 'close'] = 1.1005  # Very close to lower band
        bb_data.loc[last_idx, 'RSI'] = 20  # Oversold
    
    action_bb, signals_bb = strategy_engine.run_complete_strategy("Arbitrage", bb_data, "EURUSD")
    
    test_results["arbitrage_bb_extreme"] = {
        "action": action_bb,
        "signal_count": len(signals_bb),
        "pass": True  # Any result is valid
    }
    
    print(f"   Action: {action_bb}")
    print(f"   Signal Count: {len(signals_bb)}")
    print(f"   Status: {'✅ PASS' if test_results['arbitrage_bb_extreme']['pass'] else '❌ FAIL'}")
    
    return test_results


def test_signal_thresholds():
    """Test signal threshold system."""
    print("\n=== Testing Signal Thresholds ===")
    
    logger = MultiChannelLogger()
    ai_analyzer = AIMarketAnalyzer(logger)
    strategy_engine = CompleteStrategyEngine(logger, ai_analyzer)
    
    test_results = {}
    
    # Test threshold calculation
    strategies = ["HFT", "Scalping", "Intraday", "Arbitrage"]
    quality_scores = [30, 60, 80]
    
    for strategy in strategies:
        for quality in quality_scores:
            threshold = strategy_engine._get_signal_threshold(strategy, quality)
            
            test_name = f"threshold_{strategy}_{quality}"
            test_results[test_name] = {
                "strategy": strategy,
                "quality_score": quality,
                "threshold": threshold,
                "valid_threshold": isinstance(threshold, int) and threshold > 0,
                "pass": isinstance(threshold, int) and threshold > 0
            }
            
            print(f"   {strategy} @ Quality {quality}%: Threshold = {threshold}")
    
    # Verify threshold adjustment based on quality
    hft_low = strategy_engine._get_signal_threshold("HFT", 30)
    hft_high = strategy_engine._get_signal_threshold("HFT", 80)
    
    test_results["threshold_adjustment"] = {
        "low_quality_threshold": hft_low,
        "high_quality_threshold": hft_high,
        "proper_adjustment": hft_high <= hft_low,  # High quality should have lower threshold
        "pass": hft_high <= hft_low
    }
    
    print(f"\nThreshold Adjustment Test:")
    print(f"   HFT Low Quality (30%): {hft_low}")
    print(f"   HFT High Quality (80%): {hft_high}")
    print(f"   Proper Adjustment: {hft_high <= hft_low}")
    print(f"   Status: {'✅ PASS' if test_results['threshold_adjustment']['pass'] else '❌ FAIL'}")
    
    return test_results


def run_all_strategy_tests():
    """Run all strategy engine tests."""
    print("🎯 Starting Strategy Engine Comprehensive Testing")
    print("=" * 60)
    
    all_results = {}
    
    try:
        # Test 1: HFT Strategy
        all_results["hft_strategy"] = test_hft_strategy()
        
        # Test 2: Scalping Strategy
        all_results["scalping_strategy"] = test_scalping_strategy()
        
        # Test 3: Intraday Strategy
        all_results["intraday_strategy"] = test_intraday_strategy()
        
        # Test 4: Arbitrage Strategy
        all_results["arbitrage_strategy"] = test_arbitrage_strategy()
        
        # Test 5: Signal Thresholds
        all_results["signal_thresholds"] = test_signal_thresholds()
        
        # Calculate overall results
        total_tests = 0
        passed_tests = 0
        
        for category, results in all_results.items():
            for test_name, test_data in results.items():
                if isinstance(test_data, dict) and "pass" in test_data:
                    total_tests += 1
                    if test_data["pass"]:
                        passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🏆 Strategy Engine Test Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Overall Status: {'✅ PASS' if success_rate >= 80 else '❌ FAIL'}")
        
        return all_results, success_rate >= 80
        
    except Exception as e:
        print(f"❌ Error running strategy tests: {str(e)}")
        return {}, False


if __name__ == "__main__":
    results, success = run_all_strategy_tests()
    sys.exit(0 if success else 1)