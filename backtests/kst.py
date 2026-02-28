"""
KST - Know Sure Thing
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# KST
df['RCMA1'] = df['Close'].pct_change(10).rolling(10).mean()
df['RCMA2'] = df['Close'].pct_change(15).rolling(10).mean()
df['RCMA3'] = df['Close'].pct_change(20).rolling(10).mean()
df['RCMA4'] = df['Close'].pct_change(30).rolling(10).mean()

df['KST'] = (df['RCMA1'] * 1 + df['RCMA2'] * 2 + df['RCMA3'] * 3 + df['RCMA4'] * 4) * 100
df['Signal'] = df['KST'].rolling(9).mean()

# Buy when KST crosses above signal
df['Buy'] = (df['KST'] > df['Signal']) & (df['KST'].shift(1) <= df['Signal'].shift(1))
df['Sell'] = (df['KST'] < df['Signal']) & (df['KST'].shift(1) >= df['Signal'].shift(1))

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

r = backtest('KST')
print(f"\n=== KST ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
