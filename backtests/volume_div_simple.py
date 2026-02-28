"""
Volume Divergence - Simplified Backtest
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
print(f"Data: {len(df)} days")

# Normalized volume
df['VolNorm'] = df['Volume'] / df['Volume'].rolling(100).max() * 100

# Simple signals based on volume patterns
# Bullish: low price + low volume (exhaustion)
# Bearish: high price + high volume (distribution)

df['PriceLow'] = df['Low'].rolling(5).min()
df['VolLow'] = df['VolNorm'].rolling(5).min()

df['BullSignal'] = (df['Close'] == df['PriceLow']) & (df['VolNorm'] < df['VolLow'].shift(1) * 0.5)

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(100, len(df)):
        price = df.iloc[i]['Close']
        
        if df.iloc[i]['BullSignal'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        elif pos == 'long' and i - df.iloc[:i].shape[0] > 3:
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

r = backtest('Volume Divergence Simple')
print(f"\n=== Volume Divergence ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
