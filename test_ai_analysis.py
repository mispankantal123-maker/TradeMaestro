#!/usr/bin/env python3
"""
AI Analysis Testing Script
Tests AI market structure analysis, quality scoring, and signal enhancement
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add modules to path
sys.path.append('.')

from modules.ai_analysis import AIMarketAnalyzer
from modules.indicators import IndicatorCalculator
from modules.logging_utils import MultiChannelLogger


def create_test_data(trend="bullish", volatility="normal", length=100):
    """Create realistic test data for different market conditions."""
    np.random.seed(42)  # For reproducible tests
    
    base_price = 1.1000
    prices = [base_price]
    
    # Generate trending data
    for i in range(length - 1):
        if trend == "bullish":
            trend_factor = 0.0002 + np.random.normal(0, 0.0001)
        elif trend == "bearish":
            trend_factor = -0.0002 + np.random.normal(0, 0.0001)
        else:  # neutral
            trend_factor = np.random.normal(0, 0.0001)
        
        # Add volatility
        if volatility == "high":
            noise = np.random.normal(0, 0.0005)
        elif volatility == "low":
            noise = np.random.normal(0, 0.0001)
        else:  # normal
            noise = np.random.normal(0, 0.0003)
        
        next_price = prices[-1] + trend_factor + noise
        prices.append(max(0.9000, min(1.3000, next_price)))  # Reasonable bounds
    
    # Create OHLCV data
    data = []
    for i, close in enumerate(prices):
        high = close + np.random.uniform(0, 0.0005)
        low = close - np.random.uniform(0, 0.0005)
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


def test_ai_market_structure_analysis():
    """Test AI market structure analysis functionality."""
    print("=== Testing AI Market Structure Analysis ===")
    
    # Initialize components
    logger = MultiChannelLogger()
    ai_analyzer = AIMarketAnalyzer(logger)
    indicator_calc = IndicatorCalculator(logger, None)
    
    test_results = {}
    
    # Test Case 1: Bullish Market
    print("\n1. Testing Bullish Market Analysis...")
    bullish_data = create_test_data(trend="bullish", volatility="normal")
    bullish_data = indicator_calc.calculate_all_indicators(bullish_data)
    
    bullish_analysis = ai_analyzer.analyze_market_structure(bullish_data, "EURUSD")
    
    test_results["bullish_analysis"] = {
        "market_structure": bullish_analysis.get("market_structure"),
        "confidence": bullish_analysis.get("confidence", 0),
        "trend_strength": bullish_analysis.get("trend_strength", 0),
        "quality_factors_count": len(bullish_analysis.get("quality_factors", [])),
        "expected_structure": "BULLISH",
        "pass": bullish_analysis.get("market_structure") in ["BULLISH", "NEUTRAL"] and bullish_analysis.get("confidence", 0) > 0
    }
    
    print(f"   Market Structure: {bullish_analysis.get('market_structure', 'N/A')}")
    print(f"   Confidence: {bullish_analysis.get('confidence', 0)}%")
    print(f"   Trend Strength: {bullish_analysis.get('trend_strength', 0)}%")
    print(f"   Quality Factors: {len(bullish_analysis.get('quality_factors', []))}")
    print(f"   Status: {'✅ PASS' if test_results['bullish_analysis']['pass'] else '❌ FAIL'}")
    
    # Test Case 2: Bearish Market
    print("\n2. Testing Bearish Market Analysis...")
    bearish_data = create_test_data(trend="bearish", volatility="normal")
    bearish_data = indicator_calc.calculate_all_indicators(bearish_data)
    
    bearish_analysis = ai_analyzer.analyze_market_structure(bearish_data, "EURUSD")
    
    test_results["bearish_analysis"] = {
        "market_structure": bearish_analysis.get("market_structure"),
        "confidence": bearish_analysis.get("confidence", 0),
        "trend_strength": bearish_analysis.get("trend_strength", 0),
        "quality_factors_count": len(bearish_analysis.get("quality_factors", [])),
        "expected_structure": "BEARISH",
        "pass": bearish_analysis.get("market_structure") in ["BEARISH", "NEUTRAL"] and bearish_analysis.get("confidence", 0) > 0
    }
    
    print(f"   Market Structure: {bearish_analysis.get('market_structure', 'N/A')}")
    print(f"   Confidence: {bearish_analysis.get('confidence', 0)}%")
    print(f"   Trend Strength: {bearish_analysis.get('trend_strength', 0)}%")
    print(f"   Quality Factors: {len(bearish_analysis.get('quality_factors', []))}")
    print(f"   Status: {'✅ PASS' if test_results['bearish_analysis']['pass'] else '❌ FAIL'}")
    
    # Test Case 3: High Volatility Market
    print("\n3. Testing High Volatility Market...")
    volatile_data = create_test_data(trend="neutral", volatility="high")
    volatile_data = indicator_calc.calculate_all_indicators(volatile_data)
    
    volatile_analysis = ai_analyzer.analyze_market_structure(volatile_data, "EURUSD")
    
    test_results["volatile_analysis"] = {
        "volatility_state": volatile_analysis.get("volatility_state"),
        "confidence": volatile_analysis.get("confidence", 0),
        "expected_volatility": "HIGH",
        "pass": volatile_analysis.get("volatility_state") in ["HIGH", "NORMAL"] and volatile_analysis.get("confidence", 0) >= 0
    }
    
    print(f"   Volatility State: {volatile_analysis.get('volatility_state', 'N/A')}")
    print(f"   Confidence: {volatile_analysis.get('confidence', 0)}%")
    print(f"   Status: {'✅ PASS' if test_results['volatile_analysis']['pass'] else '❌ FAIL'}")
    
    return test_results


def test_signal_quality_scoring():
    """Test signal quality scoring system."""
    print("\n=== Testing Signal Quality Scoring ===")
    
    logger = MultiChannelLogger()
    ai_analyzer = AIMarketAnalyzer(logger)
    indicator_calc = IndicatorCalculator(logger, None)
    
    test_results = {}
    
    # Test Case 1: High Quality Signals
    print("\n1. Testing High Quality Signals...")
    high_quality_data = create_test_data(trend="bullish", volatility="normal")
    high_quality_data = indicator_calc.calculate_all_indicators(high_quality_data)
    
    market_analysis = ai_analyzer.analyze_market_structure(high_quality_data, "EURUSD")
    
    high_quality_signals = [
        "EMA5>EMA13 cross @ 1.1050",
        "RSI oversold recovery @ 25.5",
        "Volume surge UP",
        "MACD bullish momentum",
        "Bollinger breakout confirmed"
    ]
    
    high_quality_score = ai_analyzer.calculate_signal_quality_score(
        high_quality_data, high_quality_signals, market_analysis)
    
    test_results["high_quality"] = {
        "score": high_quality_score,
        "signal_count": len(high_quality_signals),
        "expected_range": (60, 100),
        "pass": 60 <= high_quality_score <= 100
    }
    
    print(f"   Signal Count: {len(high_quality_signals)}")
    print(f"   Quality Score: {high_quality_score}/100")
    print(f"   Status: {'✅ PASS' if test_results['high_quality']['pass'] else '❌ FAIL'}")
    
    # Test Case 2: Low Quality Signals
    print("\n2. Testing Low Quality Signals...")
    low_quality_data = create_test_data(trend="neutral", volatility="high")
    low_quality_data = indicator_calc.calculate_all_indicators(low_quality_data)
    
    market_analysis_low = ai_analyzer.analyze_market_structure(low_quality_data, "EURUSD")
    
    low_quality_signals = [
        "Weak signal"
    ]
    
    low_quality_score = ai_analyzer.calculate_signal_quality_score(
        low_quality_data, low_quality_signals, market_analysis_low)
    
    test_results["low_quality"] = {
        "score": low_quality_score,
        "signal_count": len(low_quality_signals),
        "expected_range": (0, 40),
        "pass": 0 <= low_quality_score <= 40
    }
    
    print(f"   Signal Count: {len(low_quality_signals)}")
    print(f"   Quality Score: {low_quality_score}/100")
    print(f"   Status: {'✅ PASS' if test_results['low_quality']['pass'] else '❌ FAIL'}")
    
    return test_results


def test_ai_signal_enhancement():
    """Test AI signal enhancement system."""
    print("\n=== Testing AI Signal Enhancement ===")
    
    logger = MultiChannelLogger()
    ai_analyzer = AIMarketAnalyzer(logger)
    indicator_calc = IndicatorCalculator(logger, None)
    
    test_results = {}
    
    # Test Case 1: Signal Enhancement with High Confidence
    print("\n1. Testing Signal Enhancement...")
    test_data = create_test_data(trend="bullish", volatility="normal")
    test_data = indicator_calc.calculate_all_indicators(test_data)
    
    market_analysis = ai_analyzer.analyze_market_structure(test_data, "EURUSD")
    
    initial_signals = [
        "Basic EMA cross",
        "RSI condition met"
    ]
    
    enhanced_signals, buy_signals, sell_signals = ai_analyzer.enhance_signals_with_ai(
        test_data, initial_signals, market_analysis, "Scalping")
    
    test_results["signal_enhancement"] = {
        "initial_count": len(initial_signals),
        "enhanced_count": len(enhanced_signals),
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "enhancement_applied": len(enhanced_signals) > len(initial_signals),
        "pass": len(enhanced_signals) >= len(initial_signals) and (buy_signals > 0 or sell_signals > 0)
    }
    
    print(f"   Initial Signals: {len(initial_signals)}")
    print(f"   Enhanced Signals: {len(enhanced_signals)}")
    print(f"   Buy Signals: {buy_signals}")
    print(f"   Sell Signals: {sell_signals}")
    print(f"   Enhancement Applied: {'Yes' if len(enhanced_signals) > len(initial_signals) else 'No'}")
    print(f"   Status: {'✅ PASS' if test_results['signal_enhancement']['pass'] else '❌ FAIL'}")
    
    return test_results


def run_all_ai_tests():
    """Run all AI analysis tests."""
    print("🤖 Starting AI Analysis Comprehensive Testing")
    print("=" * 60)
    
    all_results = {}
    
    try:
        # Test 1: Market Structure Analysis
        all_results["market_structure"] = test_ai_market_structure_analysis()
        
        # Test 2: Signal Quality Scoring
        all_results["quality_scoring"] = test_signal_quality_scoring()
        
        # Test 3: AI Signal Enhancement
        all_results["signal_enhancement"] = test_ai_signal_enhancement()
        
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
        
        print(f"\n🏆 AI Analysis Test Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Overall Status: {'✅ PASS' if success_rate >= 80 else '❌ FAIL'}")
        
        return all_results, success_rate >= 80
        
    except Exception as e:
        print(f"❌ Error running AI tests: {str(e)}")
        return {}, False


if __name__ == "__main__":
    results, success = run_all_ai_tests()
    sys.exit(0 if success else 1)