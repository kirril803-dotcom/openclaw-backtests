"""
Schaff Trend Cycle
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# MACD for STC
exp1 = df['Close'].ewm(span=23, adjust=False).mean()
exp2 = df['Close'].ewm(span=50, adjust=False).mean()
df['MACD_STC'] = exp1 - exp2

# Stochastic of MACD
cycle = 10
low_macd = df['MACD_STC'].rolling(cycle).min()
high_macd = df['MACD_STC'].rolling(cycle).max()
df['Stoch1'] = 100 * (df['MACD_STC'] - low_macd) / (high_macd - low_macd)
df['Stoch1'] = df['Stoch1'].ewm(span=3, adjust=False).mean()

# Second stochastic
low_stoch = df['Stoch1'].rolling(cycle).min()
high_stoch = df['Stoch1'].rolling(cycle).max()
df['STC'] = 100 * (df['Stoch1'] - low_stoch) / (high_stoch - low_stoch)
df['STC'] = df['STC'].ewm(span=3, adjust=False).mean()

# Buy when STC crosses above 25
df['Buy'] = (df['STC'] > 25) & (df['STC'].shift(1) <= 25)
df['Sell'] = (df['STC'] < 75) & (df['STC'].shift(1) >= 75)

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

r = backtest('STC')
print(f"\n=== STC ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
