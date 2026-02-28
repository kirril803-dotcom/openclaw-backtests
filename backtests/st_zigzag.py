"""
Supertrend + ZigZag
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# ZigZag
def zigzag(df, threshold=0.05):
    zz = []
    direction = 0
    for i in range(len(df)):
        if i < 2:
            zz.append(np.nan)
            continue
        high = df.iloc[i]['High']
        low = df.iloc[i]['Low']
        prev_high = df.iloc[i-1]['High']
        prev_low = df.iloc[i-1]['Low']
        
        if direction == 0:
            if high > prev_high:
                direction = 1
            elif low < prev_low:
                direction = -1
        elif direction == 1:
            if high > prev_high:
                zz.append(high)
            elif low < prev_low - threshold * prev_high:
                direction = -1
                zz.append(low)
            else:
                zz.append(np.nan)
        else:
            if low < prev_low:
                zz.append(low)
            elif high > prev_high + threshold * prev_low:
                direction = 1
                zz.append(high)
            else:
                zz.append(np.nan)
    return zz

df['ZigZag'] = zigzag(df)

# ATR for Supertrend
st_period = 10
df['TR2'] = np.maximum(df['High'] - df['Low'], 
                       np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                 abs(df['Low'] - df['Close'].shift(1))))
df['ATR2'] = df['TR2'].rolling(st_period).mean()

# Supertrend
multiplier = 3
df['Upper'] = (df['High'] + df['Low']) / 2 + multiplier * df['ATR2']
df['Lower'] = (df['High'] + df['Low']) / 2 - multiplier * df['ATR2']

df['ST_dir'] = 'up'
for i in range(1, len(df)):
    if df.iloc[i]['Close'] > df.iloc[i-1]['Upper']:
        df.loc[df.index[i], 'ST_dir'] = 'up'
    elif df.iloc[i]['Close'] < df.iloc[i-1]['Lower']:
        df.loc[df.index[i], 'ST_dir'] = 'down'
    else:
        df.loc[df.index[i], 'ST_dir'] = df.iloc[i-1]['ST_dir']

# Buy: ZigZag low + ST bullish
df['Buy'] = (~df['ZigZag'].isna()) & (df['ZigZag'] == df['Low']) & (df['ST_dir'] == 'up') & (df['ST_dir'].shift(1) == 'down')
df['Sell'] = (df['ST_dir'] == 'down') & (df['ST_dir'].shift(1) == 'up')

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

r = backtest('ST + ZigZag')
print(f"\n=== ST + ZigZag ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
