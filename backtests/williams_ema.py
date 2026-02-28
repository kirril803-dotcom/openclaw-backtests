"""
Williams %R + EMA
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Williams %R
period = 14
df['W%R'] = -100 * (df['High'].rolling(period).max() - df['Close']) / (df['High'].rolling(period).max() - df['Low'].rolling(period).min())

# EMA filter
df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
df['Uptrend'] = df['Close'] > df['EMA50']

# Buy when W%R crosses above -80 in uptrend
df['Buy'] = (df['W%R'] > -80) & (df['W%R'].shift(1) <= -80) & df['Uptrend']
df['Sell'] = (df['W%R'] < -20) & (df['W%R'].shift(1) >= -20)

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    
    for i in range(60, len(df)):
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

r = backtest('Williams %R + EMA')
print(f"\n=== Williams %R + EMA ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
