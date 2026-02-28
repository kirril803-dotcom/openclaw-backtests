"""
Vortex Indicator
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Vortex
period = 14
df['VM+'] = abs(df['High'] - df['Low'].shift(1))
df['VM-'] = abs(df['Low'] - df['High'].shift(1))
df['TR'] = np.maximum(df['High'] - df['Low'],
                       np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                 abs(df['Low'] - df['Close'].shift(1))))

df['VI+'] = df['VM+'].rolling(period).sum() / df['TR'].rolling(period).sum()
df['VI-'] = df['VM-'].rolling(period).sum() / df['TR'].rolling(period).sum()

# Buy when VI+ crosses above VI-
df['Buy'] = (df['VI+'] > df['VI-']) & (df['VI+'].shift(1) <= df['VI-'].shift(1))
df['Sell'] = (df['VI+'] < df['VI-']) & (df['VI+'].shift(1) >= df['VI-'].shift(1))

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

r = backtest('Vortex')
print(f"\n=== Vortex ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
