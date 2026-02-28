"""
Coppock Curve
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Coppock Curve
roc14 = ((df['Close'] - df['Close'].shift(14)) / df['Close'].shift(14)) * 100
roc11 = ((df['Close'] - df['Close'].shift(11)) / df['Close'].shift(11)) * 100
df['Coppock'] = (roc14 + roc11).rolling(10).mean()

# Buy when Coppock crosses above 0
df['Buy'] = (df['Coppock'] > 0) & (df['Coppock'].shift(1) <= 0)
df['Sell'] = (df['Coppock'] < 0) & (df['Coppock'].shift(1) >= 0)

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

r = backtest('Coppock')
print(f"\n=== Coppock ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
