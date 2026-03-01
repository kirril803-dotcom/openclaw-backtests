"""
Supertrend + KST
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# KST (Know Sure Thing)
df['MA1'] = df['Close'].rolling(10).mean()
df['MA2'] = df['Close'].rolling(15).mean()
df['MA3'] = df['Close'].rolling(20).mean()
df['MA4'] = df['Close'].rolling(30).mean()

df['ROC1'] = ((df['MA1'] - df['MA1'].shift(10)) / df['MA1'].shift(10)) * 100
df['ROC2'] = ((df['MA2'] - df['MA2'].shift(15)) / df['MA2'].shift(15)) * 100
df['ROC3'] = ((df['MA3'] - df['MA3'].shift(20)) / df['MA3'].shift(20)) * 100
df['ROC4'] = ((df['MA4'] - df['MA4'].shift(30)) / df['MA4'].shift(30)) * 100

df['KST'] = (df['ROC1'] * 1) + (df['ROC2'] * 2) + (df['ROC3'] * 3) + (df['ROC4'] * 4)
df['KST_Signal'] = df['KST'].rolling(9).mean()

# ATR for Supertrend
st_period = 10
df['TR'] = np.maximum(df['High'] - df['Low'],
                       np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                 abs(df['Low'] - df['Close'].shift(1))))
df['ATR'] = df['TR'].rolling(st_period).mean()

# Supertrend
multiplier = 3
df['ST_Upper'] = (df['High'] + df['Low']) / 2 + multiplier * df['ATR']
df['ST_Lower'] = (df['High'] + df['Low']) / 2 - multiplier * df['ATR']

df['ST_dir'] = 'up'
for i in range(1, len(df)):
    if df.iloc[i]['Close'] > df.iloc[i-1]['ST_Upper']:
        df.loc[df.index[i], 'ST_dir'] = 'up'
    elif df.iloc[i]['Close'] < df.iloc[i-1]['ST_Lower']:
        df.loc[df.index[i], 'ST_dir'] = 'down'
    else:
        df.loc[df.index[i], 'ST_dir'] = df.iloc[i-1]['ST_dir']

# Buy: KST crosses above signal + ST bullish
df['Buy'] = (df['KST'] > df['KST_Signal']) & (df['KST'].shift(1) <= df['KST_Signal'].shift(1)) & (df['ST_dir'] == 'up')
df['Sell'] = (df['KST'] < df['KST_Signal']) & (df['KST'].shift(1) >= df['KST_Signal'].shift(1)) & (df['ST_dir'] == 'down')

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

r = backtest('ST + KST')
print(f"\n=== ST + KST ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
