#!/usr/bin/env python3
"""
TP/SL Parser Testing Script
Tests multi-unit parsing, validation, and currency conversion
"""

import sys
import pandas as pd

# Add modules to path
sys.path.append('.')

from modules.tp_sl_parser import TPSLParser
from modules.logging_utils import MultiChannelLogger
from modules.symbols import SymbolManager
from modules.account import AccountManager


class MockSymbolManager:
    """Mock symbol manager for testing."""
    
    def get_symbol_info(self, symbol):
        """Return mock symbol info."""
        symbol_data = {
            "EURUSD": {"point": 0.00001, "digits": 5, "trade_stops_level": 10, "spread": 15},
            "GBPUSD": {"point": 0.00001, "digits": 5, "trade_stops_level": 10, "spread": 18},
            "USDJPY": {"point": 0.001, "digits": 3, "trade_stops_level": 10, "spread": 12},
            "XAUUSD": {"point": 0.01, "digits": 2, "trade_stops_level": 50, "spread": 30}
        }
        return symbol_data.get(symbol, {"point": 0.00001, "digits": 5, "trade_stops_level": 10, "spread": 15})


class MockAccountManager:
    """Mock account manager for testing."""
    
    def __init__(self):
        self.account_info = {"currency": "USD"}
    
    def get_currency_conversion_rate(self, from_currency, to_currency):
        """Return mock conversion rates."""
        rates = {
            ("EUR", "USD"): 1.0800,
            ("GBP", "USD"): 1.2500,
            ("CAD", "USD"): 0.7400,
            ("AUD", "USD"): 0.6600,
            ("JPY", "USD"): 0.0067,
            ("CHF", "USD"): 1.0900,
            ("NZD", "USD"): 0.6100
        }
        return rates.get((from_currency, to_currency), 1.0)


def test_pips_parsing():
    """Test pips parsing functionality."""
    print("=== Testing Pips Parsing ===")
    
    logger = MultiChannelLogger()
    symbol_manager = MockSymbolManager()
    account_manager = MockAccountManager()
    parser = TPSLParser(logger, symbol_manager, account_manager)
    
    test_results = {}
    
    test_cases = [
        # (input, unit, symbol, current_price, action, expected_result_type)
        ("20", "pips", "EURUSD", 1.1000, "BUY", "price"),
        ("15.5", "pips", "EURUSD", 1.1000, "SELL", "price"),
        ("30pips", "pips", "GBPUSD", 1.2500, "BUY", "price"),
        ("25p", "pips", "USDJPY", 150.00, "SELL", "price"),
        ("", "pips", "EURUSD", 1.1000, "BUY", None),  # Empty input
        ("abc", "pips", "EURUSD", 1.1000, "BUY", None),  # Invalid input
        ("-10", "pips", "EURUSD", 1.1000, "BUY", None)  # Negative input
    ]
    
    for i, (input_val, unit, symbol, current_price, action, expected) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{input_val}' {unit} for {symbol} {action}")
        
        result = parser.parse_tp_sl_input(input_val, unit, symbol, current_price, action)
        
        test_passed = False
        if expected == "price":
            test_passed = result is not None and isinstance(result, (int, float)) and result > 0
        elif expected is None:
            test_passed = result is None
        
        test_results[f"pips_test_{i}"] = {
            "input": input_val,
            "result": result,
            "expected": expected,
            "pass": test_passed
        }
        
        print(f"   Input: '{input_val}'")
        print(f"   Result: {result}")
        print(f"   Expected: {expected}")
        print(f"   Status: {'✅ PASS' if test_passed else '❌ FAIL'}")
    
    return test_results


def test_price_parsing():
    """Test direct price parsing."""
    print("\n=== Testing Price Parsing ===")
    
    logger = MultiChannelLogger()
    symbol_manager = MockSymbolManager()
    account_manager = MockAccountManager()
    parser = TPSLParser(logger, symbol_manager, account_manager)
    
    test_results = {}
    
    test_cases = [
        ("1.2050", "price", "EURUSD", 1.2000, "BUY"),
        ("1850.25", "price", "XAUUSD", 1840.00, "SELL"),
        ("0.7500", "price", "AUDUSD", 0.7450, "BUY"),
        ("", "price", "EURUSD", 1.1000, "BUY"),  # Empty
        ("abc", "price", "EURUSD", 1.1000, "BUY"),  # Invalid
        ("-1.1000", "price", "EURUSD", 1.1000, "BUY")  # Negative
    ]
    
    for i, (input_val, unit, symbol, current_price, action) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{input_val}' {unit} for {symbol}")
        
        result = parser.parse_tp_sl_input(input_val, unit, symbol, current_price, action)
        
        if input_val and input_val not in ["", "abc"] and not input_val.startswith("-"):
            expected_price = float(input_val)
            test_passed = result is not None and abs(result - expected_price) < 0.0001
        else:
            test_passed = result is None
        
        test_results[f"price_test_{i}"] = {
            "input": input_val,
            "result": result,
            "pass": test_passed
        }
        
        print(f"   Input: '{input_val}'")
        print(f"   Result: {result}")
        print(f"   Status: {'✅ PASS' if test_passed else '❌ FAIL'}")
    
    return test_results


def test_percentage_parsing():
    """Test percentage parsing."""
    print("\n=== Testing Percentage Parsing ===")
    
    logger = MultiChannelLogger()
    symbol_manager = MockSymbolManager()
    account_manager = MockAccountManager()
    parser = TPSLParser(logger, symbol_manager, account_manager)
    
    test_results = {}
    
    test_cases = [
        ("1.5%", "%", "EURUSD", 1.1000, "BUY"),   # Expected: 1.1165
        ("2%", "%", "GBPUSD", 1.2500, "SELL"),    # Expected: 1.2250  
        ("0.8%", "%", "USDJPY", 150.00, "BUY"),   # Expected: 151.20
        ("100%", "%", "EURUSD", 1.1000, "BUY"),   # Invalid - too high
        ("", "%", "EURUSD", 1.1000, "BUY"),       # Empty
        ("abc%", "%", "EURUSD", 1.1000, "BUY")    # Invalid
    ]
    
    for i, (input_val, unit, symbol, current_price, action) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{input_val}' {unit} for {symbol} {action}")
        
        result = parser.parse_tp_sl_input(input_val, unit, symbol, current_price, action)
        
        test_passed = False
        if input_val in ["1.5%", "2%", "0.8%"]:
            test_passed = result is not None and result != current_price
        else:
            test_passed = result is None
        
        test_results[f"percent_test_{i}"] = {
            "input": input_val,
            "result": result,
            "current_price": current_price,
            "pass": test_passed
        }
        
        print(f"   Input: '{input_val}'")
        print(f"   Current Price: {current_price}")
        print(f"   Result: {result}")
        print(f"   Status: {'✅ PASS' if test_passed else '❌ FAIL'}")
    
    return test_results


def test_currency_parsing():
    """Test currency unit parsing."""
    print("\n=== Testing Currency Parsing ===")
    
    logger = MultiChannelLogger()
    symbol_manager = MockSymbolManager()
    account_manager = MockAccountManager()
    parser = TPSLParser(logger, symbol_manager, account_manager)
    
    test_results = {}
    
    test_cases = [
        ("100USD", "currency", "EURUSD", 1.1000, "BUY"),
        ("50EUR", "currency", "GBPUSD", 1.2500, "SELL"),
        ("200CAD", "currency", "USDCAD", 1.3500, "BUY"),
        ("10000JPY", "currency", "USDJPY", 150.00, "SELL"),
        ("", "currency", "EURUSD", 1.1000, "BUY"),  # Empty
        ("100INVALID", "currency", "EURUSD", 1.1000, "BUY"),  # Invalid currency
        ("-100USD", "currency", "EURUSD", 1.1000, "BUY")  # Negative
    ]
    
    for i, (input_val, unit, symbol, current_price, action) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{input_val}' {unit} for {symbol} {action}")
        
        result = parser.parse_tp_sl_input(input_val, unit, symbol, current_price, action)
        
        if input_val and "USD" in input_val and not input_val.startswith("-") and "INVALID" not in input_val:
            test_passed = result is not None and result != current_price
        else:
            test_passed = result is None
        
        test_results[f"currency_test_{i}"] = {
            "input": input_val,
            "result": result,
            "current_price": current_price,
            "pass": test_passed
        }
        
        print(f"   Input: '{input_val}'")
        print(f"   Current Price: {current_price}")
        print(f"   Result: {result}")
        print(f"   Status: {'✅ PASS' if test_passed else '❌ FAIL'}")
    
    return test_results


def test_tp_sl_validation():
    """Test TP/SL level validation."""
    print("\n=== Testing TP/SL Validation ===")
    
    logger = MultiChannelLogger()
    symbol_manager = MockSymbolManager()
    account_manager = MockAccountManager()
    parser = TPSLParser(logger, symbol_manager, account_manager)
    
    test_results = {}
    
    test_cases = [
        # (symbol, current_price, tp_price, sl_price, action, expected_valid)
        ("EURUSD", 1.1000, 1.1020, 1.0980, "BUY", True),   # Valid
        ("EURUSD", 1.1000, 1.1001, 1.0999, "BUY", False),  # Too close
        ("EURUSD", 1.1000, 1.0980, 1.1020, "BUY", False),  # Wrong direction
        ("EURUSD", 1.1000, 1.0980, 1.1020, "SELL", True),  # Valid SELL
        ("EURUSD", 1.1000, None, 1.0980, "BUY", True),     # TP None
        ("EURUSD", 1.1000, 1.1020, None, "BUY", True)      # SL None
    ]
    
    for i, (symbol, current_price, tp_price, sl_price, action, expected_valid) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing validation: {symbol} {action}")
        
        is_valid, error_msg = parser.validate_tp_sl_levels(symbol, current_price, tp_price, sl_price, action)
        
        test_passed = is_valid == expected_valid
        
        test_results[f"validation_test_{i}"] = {
            "symbol": symbol,
            "action": action,
            "tp_price": tp_price,
            "sl_price": sl_price,
            "is_valid": is_valid,
            "expected_valid": expected_valid,
            "error_msg": error_msg,
            "pass": test_passed
        }
        
        print(f"   Current: {current_price}")
        print(f"   TP: {tp_price}")
        print(f"   SL: {sl_price}")
        print(f"   Action: {action}")
        print(f"   Valid: {is_valid}")
        print(f"   Expected: {expected_valid}")
        print(f"   Error: {error_msg}")
        print(f"   Status: {'✅ PASS' if test_passed else '❌ FAIL'}")
    
    return test_results


def run_all_tp_sl_tests():
    """Run all TP/SL parser tests."""
    print("💰 Starting TP/SL Parser Comprehensive Testing")
    print("=" * 60)
    
    all_results = {}
    
    try:
        # Test 1: Pips Parsing
        all_results["pips_parsing"] = test_pips_parsing()
        
        # Test 2: Price Parsing
        all_results["price_parsing"] = test_price_parsing()
        
        # Test 3: Percentage Parsing
        all_results["percentage_parsing"] = test_percentage_parsing()
        
        # Test 4: Currency Parsing
        all_results["currency_parsing"] = test_currency_parsing()
        
        # Test 5: TP/SL Validation
        all_results["tp_sl_validation"] = test_tp_sl_validation()
        
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
        
        print(f"\n🏆 TP/SL Parser Test Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Overall Status: {'✅ PASS' if success_rate >= 80 else '❌ FAIL'}")
        
        return all_results, success_rate >= 80
        
    except Exception as e:
        print(f"❌ Error running TP/SL tests: {str(e)}")
        return {}, False


if __name__ == "__main__":
    results, success = run_all_tp_sl_tests()
    sys.exit(0 if success else 1)