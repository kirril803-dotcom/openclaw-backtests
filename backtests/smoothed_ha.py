"""
Smoothed Heikin Ashi
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Heikin Ashi
df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
df['HA_Open'] = df['Open'].copy()
for i in range(1, len(df)):
    df.loc[df.index[i], 'HA_Open'] = (df.iloc[i-1]['HA_Open'] + df.iloc[i-1]['HA_Close']) / 2

df['HA_High'] = df[['High', 'HA_Open', 'HA_Close']].max(axis=1)
df['HA_Low'] = df[['Low', 'HA_Open', 'HA_Close']].min(axis=1)

# Smoothed HA
df['SHA_Close'] = df['HA_Close'].ewm(span=10, adjust=False).mean()
df['SHA_Open'] = df['HA_Open'].ewm(span=10, adjust=False).mean()

# Buy: green HA candle
df['Buy'] = (df['SHA_Close'] > df['SHA_Open']) & (df['SHA_Close'].shift(1) <= df['SHA_Open'].shift(1))
df['Sell'] = (df['SHA_Close'] < df['SHA_Open']) & (df['SHA_Close'].shift(1) >= df['SHA_Open'].shift(1))

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

r = backtest('Smoothed HA')
print(f"\n=== Smoothed HA ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
