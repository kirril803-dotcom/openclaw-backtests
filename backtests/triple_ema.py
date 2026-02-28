"""
Triple EMA
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Triple EMA
df['EMA8'] = df['Close'].ewm(span=8, adjust=False).mean()
df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
df['EMA55'] = df['Close'].ewm(span=55, adjust=False).mean()

# Buy: EMA8 > EMA21 > EMA55 (all aligned)
df['Trend'] = (df['EMA8'] > df['EMA21']) & (df['EMA21'] > df['EMA55'])
df['TrendDown'] = (df['EMA8'] < df['EMA21']) & (df['EMA21'] < df['EMA55'])

df['Buy'] = df['Trend'] & (df['Trend'].shift(1) == False)
df['Sell'] = df['TrendDown'] & (df['TrendDown'].shift(1) == False)

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

r = backtest('Triple EMA')
print(f"\n=== Triple EMA ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
