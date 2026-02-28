"""
CCI - Commodity Channel Index
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# CCI
period = 20
df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
df['SMA_TP'] = df['TP'].rolling(period).mean()
df['MAD'] = df['TP'].rolling(period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
df['CCI'] = (df['TP'] - df['SMA_TP']) / (0.015 * df['MAD'])

# Buy when CCI crosses above -100, sell when crosses below +100
df['Buy'] = (df['CCI'] > -100) & (df['CCI'].shift(1) <= -100)
df['Sell'] = (df['CCI'] < 100) & (df['CCI'].shift(1) >= 100)

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

r = backtest('CCI')
print(f"\n=== CCI ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
