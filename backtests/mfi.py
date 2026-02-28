"""
MFI - Money Flow Index
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# MFI
period = 14
df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
df['MF'] = df['TP'] * df['Volume']
df['PMF'] = np.where(df['TP'] > df['TP'].shift(1), df['MF'], 0)
df['NMF'] = np.where(df['TP'] < df['TP'].shift(1), df['MF'], 0)
df['MFR'] = df['PMF'].rolling(period).sum() / df['NMF'].rolling(period).sum()
df['MFI'] = 100 - (100 / (1 + df['MFR']))

# Buy when MFI crosses above 20, sell when crosses below 80
df['Buy'] = (df['MFI'] > 20) & (df['MFI'].shift(1) <= 20)
df['Sell'] = (df['MFI'] < 80) & (df['MFI'].shift(1) >= 80)

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

r = backtest('MFI')
print(f"\n=== MFI ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
