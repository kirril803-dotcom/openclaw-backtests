"""
Trend Line Breakout
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Connect last 20 highs/lows to form trend lines
# Simplified: use highest high / lowest low of last 20 bars
period = 20
df['HH'] = df['High'].rolling(period).max()
df['LL'] = df['Low'].rolling(period).min()

# Buy when price breaks above HH, sell when breaks below LL
df['Buy'] = (df['Close'] > df['HH'].shift(1)) & (df['Close'].shift(1) <= df['HH'].shift(1))
df['Sell'] = (df['Close'] < df['LL'].shift(1)) & (df['Close'].shift(1) >= df['LL'].shift(1))

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        if pos is None and df.iloc[i]['Buy']:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        elif pos == 'long' and df.iloc[i]['Sell']:
            cash = btc * price
            pos = None
            btc = 0
    
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    return {'name': name, 'roi': roi, 'trades': trades}

r = backtest('Trend Line Break')
print(f"\n=== Trend Line Break ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
