"""
VWAP Strategy
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# VWAP - reset each day
df['Typical'] = (df['High'] + df['Low'] + df['Close']) / 3
df['VWAP'] = df['Typical'].expanding().sum() / df['Volume'].expanding().sum() * df['Volume']

# Buy when price crosses above VWAP, sell when crosses below
df['Buy'] = (df['Close'] > df['VWAP']) & (df['Close'].shift(1) <= df['VWAP'].shift(1))
df['Sell'] = (df['Close'] < df['VWAP']) & (df['Close'].shift(1) >= df['VWAP'].shift(1))

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

r = backtest('VWAP Crossover')
print(f"\n=== VWAP ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
