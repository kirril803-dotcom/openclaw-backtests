"""
Stochastic Oscillator Strategy
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Stochastic
low14 = df['Low'].rolling(14).min()
high14 = df['High'].rolling(14).max()
df['K'] = 100 * (df['Close'] - low14) / (high14 - low14)
df['D'] = df['K'].rolling(3).mean()

# Buy: K crosses above D below 20, Sell: K crosses below D above 80
df['Buy'] = (df['K'] > df['D']) & (df['K'].shift(1) <= df['D'].shift(1)) & (df['K'] < 30)
df['Sell'] = (df['K'] < df['D']) & (df['K'].shift(1) >= df['D'].shift(1)) & (df['K'] > 70)

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

r = backtest('Stochastic Osc')
print(f"\n=== Stochastic ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
