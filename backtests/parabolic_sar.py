"""
Parabolic SAR Reversal
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Simple Parabolic SAR approximation
af = 0.02
af_max = 0.2
df['SAR'] = df['Close'].copy()
df['Trend'] = 1  # 1 = up, -1 = down

for i in range(2, len(df)):
    if df.iloc[i-1]['Trend'] == 1:
        df.loc[df.index[i], 'SAR'] = df.iloc[i-1]['SAR'] + af * (df.iloc[i-1]['High'] - df.iloc[i-1]['SAR'])
        if df.iloc[i]['Low'] < df.iloc[i]['SAR']:
            df.loc[df.index[i], 'Trend'] = -1
    else:
        df.loc[df.index[i], 'SAR'] = df.iloc[i-1]['SAR'] + af * (df.iloc[i-1]['SAR'] - df.iloc[i-1]['Low'])
        if df.iloc[i]['High'] > df.iloc[i]['SAR']:
            df.loc[df.index[i], 'Trend'] = 1

# Buy when SAR crosses below price, sell when SAR crosses above
df['Buy'] = (df['SAR'] < df['Close']) & (df['SAR'].shift(1) >= df['Close'].shift(1)) & (df['Trend'] == 1)
df['Sell'] = (df['SAR'] > df['Close']) & (df['SAR'].shift(1) <= df['Close'].shift(1)) & (df['Trend'] == -1)

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

r = backtest('Parabolic SAR')
print(f"\n=== Parabolic SAR ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
