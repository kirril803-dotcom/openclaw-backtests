"""
Supertrend + Ultimate Oscillator
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Ultimate Oscillator
period1 = 7
period2 = 14
period3 = 28

def ultimate_osc(df, p1=7, p2=14, p3=28):
    # Prior Close
    prev_close = df['Close'].shift(1)
    
    # Buying Pressure
    bp = df['Close'] - pd.concat([df['Low'], prev_close], axis=1).min(axis=1)
    
    # True Range
    tr = pd.concat([df['High'], prev_close], axis=1).max(axis=1) - pd.concat([df['Low'], prev_close], axis=1).min(axis=1)
    
    # Average1, Average2, Average3
    avg1 = bp.rolling(p1).sum() / tr.rolling(p1).sum()
    avg2 = bp.rolling(p2).sum() / tr.rolling(p2).sum()
    avg3 = bp.rolling(p3).sum() / tr.rolling(p3).sum()
    
    # Ultimate Oscillator
    uo = 100 * ((4 * avg1) + (2 * avg2) + avg3) / (4 + 2 + 1)
    return uo

df['UO'] = ultimate_osc(df)

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

# Buy: UO < 30 + crosses above + ST bullish
df['Buy'] = (df['UO'] > 30) & (df['UO'].shift(1) <= 30) & (df['ST_dir'] == 'up')
df['Sell'] = (df['UO'] > 70) & (df['UO'].shift(1) <= 70) & (df['ST_dir'] == 'down')

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

r = backtest('ST + Ultimate Osc')
print(f"\n=== ST + Ultimate Osc ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
