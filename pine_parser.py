"""
Pine Script Parser - Extract indicators from TradingView Pine Scripts
Parse Pine Scripts and create backtests from them
"""
import pandas as pd
import numpy as np
import re

# Pine Scripts to parse
PINE_FILES = [
    'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/pine_scripts/tasc_2026_03_one_percent_a_week.pine',
    'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/pine_scripts/AlgoFox_MultiTF_SuperTrend_v1.5.pine',
]

def parse_pine_indicators(pine_code):
    """Extract indicators from Pine Script code"""
    indicators = []
    
    # Find ta. functions
    ta_functions = re.findall(r'ta\.(\w+)\s*\(', pine_code)
    indicators.extend(ta_functions)
    
    # Find built-in functions
    builtins = re.findall(r'(ta\.supertrend|ta\.sma|ta\.ema|ta\.rma|ta\.wma|ta\.vwma|ta\.atr|ta\.rsi|ta\.cci|ta\.mfi|ta\.stoch|ta\.macd|ta\.rsi|ta\.obv|ta\.vwap)', pine_code)
    indicators.extend(builtins)
    
    return list(set(indicators))

def parse_pine_strategy(pine_code):
    """Extract strategy logic from Pine Script"""
    strategy_info = {
        'name': 'Unknown',
        'indicators': [],
        'buy_conditions': [],
        'sell_conditions': [],
        'parameters': {}
    }
    
    # Get strategy name
    name_match = re.search(r'strategy\s*\(\s*["\']([^"\']+)', pine_code)
    if name_match:
        strategy_info['name'] = name_match.group(1)
    
    # Get indicators
    strategy_info['indicators'] = parse_pine_indicators(pine_code)
    
    # Find input parameters
    inputs = re.findall(r'input\.(string|int|float|bool)\s*\(\s*title\s*=\s*["\']([^"\']+)', pine_code)
    for inp_type, inp_name in inputs:
        strategy_info['parameters'][inp_name] = inp_type
    
    return strategy_info

# Parse all Pine Scripts
all_strategies = []

for filepath in PINE_FILES:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            pine_code = f.read()
        
        info = parse_pine_strategy(pine_code)
        all_strategies.append(info)
        
        print(f"\n=== {info['name']} ===")
        print(f"File: {filepath}")
        print(f"Indicators found: {info['indicators']}")
        print(f"Parameters: {list(info['parameters'].keys())[:10]}")
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")

# Save parsed info
print("\n\n=== SUMMARY OF PARSED STRATEGIES ===")
for s in all_strategies:
    print(f"\n{s['name']}:")
    print(f"  Indicators: {s['indicators']}")
