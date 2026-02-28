"""
Volume Divergence Reversal - Backtest
Simplified version using normalized volume divergence
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
print(f"Data: {len(df)} days")

# Normalized volume (0-100 scale)
normLength = 100
df['VolNorm'] = df['Volume'] / df['Volume'].rolling(normLength).max() * 100

# Pivot detection for volume
def pivothigh(series, left, right):
    """Find pivot highs"""
    highs = []
    for i in range(left, len(series) - right):
        is_high = True
        for j in range(1, left + 1):
            if series.iloc[i] <= series.iloc[i - j]:
                is_high = False
                break
        for j in range(1, right + 1):
            if series.iloc[i] <= series.iloc[i + j]:
                is_high = False
                break
        if is_high:
            highs.append(i)
    return highs

def pivotlow(series, left, right):
    lows = []
    for i in range(left, len(series) - right):
        is_low = True
        for j in range(1, left + 1):
            if series.iloc[i] >= series.iloc[i - j]:
                is_low = False
                break
        for j in range(1, right + 1):
            if series.iloc[i] >= series.iloc[i + j]:
                is_low = False
                break
        if is_low:
            lows.append(i)
    return lows

lookbackLeft = 5
lookbackRight = 2

# Find divergence signals
# Bullish: price makes lower low, volume makes higher low
# Bearish: price makes higher high, volume makes lower high

df['BullSignal'] = False
df['BearSignal'] = False

for i in range(50, len(df) - lookbackRight):
    # Check for pivot low in price
    price_lows = pivotlow(df['Low'], lookbackLeft, lookbackRight)
    vol_lows = pivotlow(df['VolNorm'], lookbackLeft, lookbackRight)
    
    # Check pivot high
    price_highs = pivothigh(df['High'], lookbackLeft, lookbackRight)
    vol_highs = pivothigh(df['VolNorm'], lookbackLeft, lookbackRight)
    
    current_idx = i
    
    # Bullish divergence: price LL but volume HL
    for pl in price_lows:
        if pl == current_idx - lookbackRight:
            # Price made low
            price_low_val = df.iloc[pl]['Low']
            # Check for earlier low
            for vl in vol_lows:
                if vl < pl:
                    vol_low_val = df.iloc[vl]['VolNorm']
                    # Check if volume low is higher than previous
                    if vol_low_val > df.iloc[pl]['VolNorm']:
                        df.at[df.index[i], 'BullSignal'] = True

    # Bearish divergence: price HH but volume LH
    for ph in price_highs:
        if ph == current_idx - lookbackRight:
            price_high_val = df.iloc[ph]['High']
            for vh in vol_highs:
                if vh < ph:
                    vol_high_val = df.iloc[vh]['VolNorm']
                    if vol_high_val < df.iloc[ph]['VolNorm']:
                        df.at[df.index[i], 'BearSignal'] = True

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(100, len(df)):
        price = df.iloc[i]['Close']
        
        # Bullish signal -> Buy
        if df.iloc[i]['BullSignal'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        # Bearish signal or after 5 bars -> Sell
        elif pos == 'long':
            if df.iloc[i]['BearSignal'] or (i - df.iloc[:i].iloc[::-1].index.get_loc(df.index[i]) > 5):
                cash = btc * price
                if price > df.iloc[i-1]['Close']:
                    wins += 1
                pos = None
                btc = 0
    
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    win_rate = wins / trades * 100 if trades > 0 else 0
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': win_rate}

r = backtest('Volume Divergence')
print(f"\n=== Volume Divergence ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
