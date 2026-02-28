"""
EMA Rainbow
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Rainbow EMAs
df['EMA5'] = df['Close'].ewm(span=5, adjust=False).mean()
df['EMA8'] = df['Close'].ewm(span=8, adjust=False).mean()
df['EMA13'] = df['Close'].ewm(span=13, adjust=False).mean()
df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
df['EMA34'] = df['Close'].ewm(span=34, adjust=False).mean()

# All EMAs aligned bullish
df['Bullish'] = (df['EMA5'] > df['EMA8']) & (df['EMA8'] > df['EMA13']) & (df['EMA13'] > df['EMA21']) & (df['EMA21'] > df['EMA34'])
df['Bearish'] = (df['EMA5'] < df['EMA8']) & (df['EMA8'] < df['EMA13']) & (df['EMA13'] < df['EMA21']) & (df['EMA21'] < df['EMA34'])

df['Buy'] = df['Bullish'] & (df['Bullish'].shift(1) == False)
df['Sell'] = df['Bearish'] & (df['Bearish'].shift(1) == False)

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

r = backtest('EMA Rainbow')
print(f"\n=== EMA Rainbow ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
