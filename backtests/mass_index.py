"""
Mass Index
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Mass Index
period1 = 9
period2 = 25

df['HL'] = df['High'] - df['Low']
df['EMA1'] = df['HL'].ewm(span=period1, adjust=False).mean()
df['EMA2'] = df['EMA1'].ewm(span=period1, adjust=False).mean()
df['Mass'] = df['EMA2'].rolling(period2).sum()

# Buy when Mass crosses above 27 (bulge), sell when crosses below 26.5
df['Buy'] = (df['Mass'] > 27) & (df['Mass'].shift(1) <= 27)
df['Sell'] = (df['Mass'] < 26.5) & (df['Mass'].shift(1) >= 26.5)

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

r = backtest('Mass Index')
print(f"\n=== Mass Index ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
