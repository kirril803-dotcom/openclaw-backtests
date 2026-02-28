"""
Ultimate Oscillator
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Ultimate Oscillator
period1 = 7
period2 = 14
period3 = 28

df['BP'] = df['Close'] - df[['Low', 'Close']].shift(1).min(axis=1)
df['TR'] = df[['High', 'Close']].max(axis=1) - df[['Low', 'Close']].min(axis=1)

df['Avg1'] = df['BP'].rolling(period1).sum() / df['TR'].rolling(period1).sum()
df['Avg2'] = df['BP'].rolling(period2).sum() / df['TR'].rolling(period2).sum()
df['Avg3'] = df['BP'].rolling(period3).sum() / df['TR'].rolling(period3).sum()

df['UO'] = 100 * ((4 * df['Avg1'] + 2 * df['Avg2'] + df['Avg3']) / 7)

# Buy when UO crosses above 30, sell when crosses below 70
df['Buy'] = (df['UO'] > 30) & (df['UO'].shift(1) <= 30)
df['Sell'] = (df['UO'] < 70) & (df['UO'].shift(1) >= 70)

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

r = backtest('Ultimate Osc')
print(f"\n=== Ultimate Oscillator ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
