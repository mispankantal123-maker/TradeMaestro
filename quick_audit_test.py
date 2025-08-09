#!/usr/bin/env python3
"""
Quick Audit Test - Simplified testing for core functionality verification
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Add modules to path
sys.path.append('.')

print("🔍 MT5 Trading Bot - Quick Audit Test")
print("=" * 50)

# Test 1: Module Imports
print("\n1. Testing Module Imports...")
import_results = {}

try:
    from modules.ai_analysis import AIMarketAnalyzer
    import_results['ai_analysis'] = True
    print("   ✅ AI Analysis module imported successfully")
except Exception as e:
    import_results['ai_analysis'] = False
    print(f"   ❌ AI Analysis import failed: {str(e)}")

try:
    from modules.tp_sl_parser import TPSLParser
    import_results['tp_sl_parser'] = True
    print("   ✅ TP/SL Parser module imported successfully")
except Exception as e:
    import_results['tp_sl_parser'] = False
    print(f"   ❌ TP/SL Parser import failed: {str(e)}")

try:
    from modules.complete_strategy import CompleteStrategyEngine
    import_results['complete_strategy'] = True
    print("   ✅ Complete Strategy Engine imported successfully")
except Exception as e:
    import_results['complete_strategy'] = False
    print(f"   ❌ Complete Strategy import failed: {str(e)}")

try:
    from modules.config_manager import ConfigManager
    import_results['config_manager'] = True
    print("   ✅ Configuration Manager imported successfully")
except Exception as e:
    import_results['config_manager'] = False
    print(f"   ❌ Configuration Manager import failed: {str(e)}")

try:
    from modules.indicators import IndicatorCalculator
    import_results['indicators'] = True
    print("   ✅ Indicators module imported successfully")
except Exception as e:
    import_results['indicators'] = False
    print(f"   ❌ Indicators import failed: {str(e)}")

# Test 2: Basic Functionality
print("\n2. Testing Basic Functionality...")

# Create sample data
np.random.seed(42)
sample_data = pd.DataFrame({
    'open': np.random.uniform(1.1000, 1.1050, 50),
    'high': np.random.uniform(1.1030, 1.1080, 50),
    'low': np.random.uniform(1.0980, 1.1020, 50),
    'close': np.random.uniform(1.1000, 1.1050, 50),
    'volume': np.random.uniform(1000, 5000, 50)
})

functionality_results = {}

# Test AI Analysis
if import_results.get('ai_analysis', False):
    try:
        # Create a simple logger mock
        class SimpleLogger:
            def log(self, message): pass
            
        ai_analyzer = AIMarketAnalyzer(SimpleLogger())
        
        # Test market structure analysis
        mock_data = sample_data.copy()
        # Add some required indicators
        mock_data['EMA5'] = 1.1025
        mock_data['EMA13'] = 1.1020
        mock_data['EMA20'] = 1.1015
        mock_data['EMA50'] = 1.1010
        mock_data['RSI'] = 55
        mock_data['MACD'] = 0.0001
        mock_data['MACD_signal'] = 0.0002
        
        result = ai_analyzer.analyze_market_structure(mock_data, "EURUSD")
        functionality_results['ai_analysis'] = isinstance(result, dict)
        print(f"   ✅ AI Analysis working: {type(result).__name__}")
        
    except Exception as e:
        functionality_results['ai_analysis'] = False
        print(f"   ❌ AI Analysis test failed: {str(e)}")

# Test TP/SL Parser
if import_results.get('tp_sl_parser', False):
    try:
        class MockSymbolManager:
            def get_symbol_info(self, symbol):
                return {"point": 0.00001, "digits": 5, "trade_stops_level": 10, "spread": 15}
        
        class MockAccountManager:
            def __init__(self):
                self.account_info = {"currency": "USD"}
            def get_currency_conversion_rate(self, from_curr, to_curr):
                return 1.0
                
        parser = TPSLParser(SimpleLogger(), MockSymbolManager(), MockAccountManager())
        
        # Test pips parsing
        result = parser.parse_tp_sl_input("20", "pips", "EURUSD", 1.1000, "BUY")
        functionality_results['tp_sl_parser'] = result is not None
        print(f"   ✅ TP/SL Parser working: {result}")
        
    except Exception as e:
        functionality_results['tp_sl_parser'] = False
        print(f"   ❌ TP/SL Parser test failed: {str(e)}")

# Test Configuration Manager
if import_results.get('config_manager', False):
    try:
        config_manager = ConfigManager(SimpleLogger())
        config = config_manager.load_config()
        functionality_results['config_manager'] = isinstance(config, dict)
        print(f"   ✅ Configuration Manager working: {len(config)} sections loaded")
        
    except Exception as e:
        functionality_results['config_manager'] = False
        print(f"   ❌ Configuration Manager test failed: {str(e)}")

# Test 3: Integration Test
print("\n3. Testing Integration...")

integration_results = {}

if all([import_results.get('ai_analysis', False), 
        import_results.get('complete_strategy', False),
        import_results.get('indicators', False)]):
    try:
        # Test full integration
        ai_analyzer = AIMarketAnalyzer(SimpleLogger())
        strategy_engine = CompleteStrategyEngine(SimpleLogger(), ai_analyzer)
        
        # Create enhanced test data
        test_data = sample_data.copy()
        
        # Add all required indicators for strategy
        test_data['EMA5'] = np.linspace(1.1000, 1.1025, 50)
        test_data['EMA8'] = np.linspace(1.0998, 1.1023, 50)
        test_data['EMA13'] = np.linspace(1.0995, 1.1020, 50)
        test_data['EMA20'] = np.linspace(1.0990, 1.1015, 50)
        test_data['EMA50'] = np.linspace(1.0985, 1.1010, 50)
        test_data['EMA200'] = np.linspace(1.0980, 1.1005, 50)
        test_data['RSI'] = np.random.uniform(30, 70, 50)
        test_data['RSI7'] = np.random.uniform(25, 75, 50)
        test_data['MACD'] = np.random.uniform(-0.0005, 0.0005, 50)
        test_data['MACD_signal'] = np.random.uniform(-0.0003, 0.0003, 50)
        test_data['MACD_histogram'] = test_data['MACD'] - test_data['MACD_signal']
        test_data['BB_upper'] = test_data['close'] + 0.0020
        test_data['BB_lower'] = test_data['close'] - 0.0020
        test_data['BB_middle'] = test_data['close']
        test_data['volume_surge'] = False
        test_data['Strong_Bullish_Candle'] = False
        test_data['Strong_Bearish_Candle'] = False
        
        # Test each strategy
        strategies = ["HFT", "Scalping", "Intraday", "Arbitrage"]
        strategy_results = {}
        
        for strategy in strategies:
            try:
                action, signals = strategy_engine.run_complete_strategy(strategy, test_data, "EURUSD")
                strategy_results[strategy] = {
                    'action': action,
                    'signal_count': len(signals) if signals else 0,
                    'working': True
                }
                print(f"   ✅ {strategy} strategy: {action} ({len(signals) if signals else 0} signals)")
            except Exception as e:
                strategy_results[strategy] = {
                    'action': None,
                    'signal_count': 0,
                    'working': False,
                    'error': str(e)
                }
                print(f"   ❌ {strategy} strategy failed: {str(e)}")
        
        integration_results['strategy_engine'] = any(s['working'] for s in strategy_results.values())
        
    except Exception as e:
        integration_results['strategy_engine'] = False
        print(f"   ❌ Integration test failed: {str(e)}")

# Test 4: Performance Check
print("\n4. Performance Check...")

try:
    import time
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    start_time = time.time()
    
    # Run intensive operations
    for i in range(10):
        if import_results.get('ai_analysis', False):
            ai_analyzer = AIMarketAnalyzer(SimpleLogger())
            result = ai_analyzer.analyze_market_structure(sample_data, "EURUSD")
    
    end_time = time.time()
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    execution_time = end_time - start_time
    memory_growth = final_memory - initial_memory
    
    performance_results = {
        'execution_time': execution_time,
        'memory_growth': memory_growth,
        'memory_efficient': memory_growth < 10,  # Less than 10MB growth
        'fast_execution': execution_time < 5.0   # Less than 5 seconds
    }
    
    print(f"   Execution Time: {execution_time:.2f} seconds")
    print(f"   Memory Growth: {memory_growth:.1f} MB")
    print(f"   Performance: {'✅ GOOD' if performance_results['memory_efficient'] and performance_results['fast_execution'] else '⚠️ SLOW'}")
    
except Exception as e:
    performance_results = {'error': str(e)}
    print(f"   ❌ Performance test failed: {str(e)}")

# Final Summary
print("\n" + "=" * 50)
print("🏆 AUDIT SUMMARY")
print("=" * 50)

total_import_tests = len(import_results)
passed_import_tests = sum(import_results.values())

total_functionality_tests = len(functionality_results) 
passed_functionality_tests = sum(functionality_results.values())

print(f"Module Imports: {passed_import_tests}/{total_import_tests} ({'✅ PASS' if passed_import_tests >= 4 else '❌ FAIL'})")
print(f"Basic Functionality: {passed_functionality_tests}/{total_functionality_tests} ({'✅ PASS' if passed_functionality_tests >= 2 else '❌ FAIL'})")
print(f"Integration: {'✅ PASS' if integration_results.get('strategy_engine', False) else '❌ FAIL'}")

# Calculate overall score
total_tests = total_import_tests + total_functionality_tests + 1  # +1 for integration
passed_tests = passed_import_tests + passed_functionality_tests + (1 if integration_results.get('strategy_engine', False) else 0)

success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

print(f"\nOverall Success Rate: {success_rate:.1f}%")
print(f"Production Readiness: {'✅ READY' if success_rate >= 80 else '❌ NOT READY'}")

# Detailed results for debugging
if success_rate < 80:
    print("\n🔍 DETAILED FAILURE ANALYSIS:")
    for module, status in import_results.items():
        if not status:
            print(f"   ❌ Import failure: {module}")
    for test, status in functionality_results.items():
        if not status:
            print(f"   ❌ Functionality failure: {test}")
    if not integration_results.get('strategy_engine', False):
        print(f"   ❌ Integration failure: strategy_engine")

print("\n" + "=" * 50)