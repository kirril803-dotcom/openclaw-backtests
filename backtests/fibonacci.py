"""
Fibonacci Retracement
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Fibonacci Retracement levels
period = 50
df['HighMax'] = df['High'].rolling(period).max()
df['LowMin'] = df['Low'].rolling(period).min()
df['Diff'] = df['HighMax'] - df['LowMin']

df['Fibo382'] = df['HighMax'] - 0.382 * df['Diff']
df['Fibo618'] = df['HighMax'] - 0.618 * df['Diff']

# Buy when price touches 61.8% retracement, sell when touches 38.2%
df['Buy'] = (df['Close'] <= df['Fibo618']) & (df['Close'].shift(1) > df['Fibo618'])
df['Sell'] = (df['Close'] >= df['Fibo382']) & (df['Close'].shift(1) < df['Fibo382'])

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

r = backtest('Fibonacci')
print(f"\n=== Fibonacci ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
