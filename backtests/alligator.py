"""
Alligator + Fractals
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Alligator
df['Jaw'] = df['Close'].ewm(span=13, adjust=False).mean().shift(8)
df['Teeth'] = df['Close'].ewm(span=8, adjust=False).mean().shift(5)
df['Lips'] = df['Close'].ewm(span=5, adjust=False).mean().shift(3)

# Buy when Alligator wakes up (Lips > Teeth > Jaw)
df['Buy'] = (df['Lips'] > df['Teeth']) & (df['Teeth'] > df['Jaw']) & ((df['Lips'].shift(1) <= df['Teeth'].shift(1)) | (df['Teeth'].shift(1) <= df['Jaw'].shift(1)))
df['Sell'] = (df['Lips'] < df['Teeth']) & (df['Teeth'] < df['Jaw']) & ((df['Lips'].shift(1) >= df['Teeth'].shift(1)) | (df['Teeth'].shift(1) >= df['Jaw'].shift(1)))

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

r = backtest('Alligator')
print(f"\n=== Alligator ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
