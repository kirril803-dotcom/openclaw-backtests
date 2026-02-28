"""
TSI - True Strength Index
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# TSI
r = 25
s = 13
pc = df['Close'].diff()
df['PC_EMA1'] = pc.ewm(span=r, adjust=False).mean()
df['PC_EMA2'] = df['PC_EMA1'].ewm(span=s, adjust=False).mean()
df['APC_EMA1'] = abs(pc).ewm(span=r, adjust=False).mean()
df['APC_EMA2'] = df['APC_EMA1'].ewm(span=s, adjust=False).mean()
df['TSI'] = 100 * df['PC_EMA2'] / df['APC_EMA2']
df['TSI_Signal'] = df['TSI'].ewm(span=7, adjust=False).mean()

# Buy when TSI crosses above signal
df['Buy'] = (df['TSI'] > df['TSI_Signal']) & (df['TSI'].shift(1) <= df['TSI_Signal'].shift(1))
df['Sell'] = (df['TSI'] < df['TSI_Signal']) & (df['TSI'].shift(1) >= df['TSI_Signal'].shift(1))

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

result = backtest('TSI')
print(f"\n=== TSI ===")
print(f"ROI: {result['roi']:.2f}% | Trades: {result['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([result['name'], f"{result['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", result['trades']])
print("Saved!")
