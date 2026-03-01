"""
Supertrend + Price Oscillator
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Price Oscillator
period = 14
df['MA_Fast'] = df['Close'].rolling(period).mean()
df['MA_Slow'] = df['Close'].rolling(period * 2).mean()
df['PriceOsc'] = ((df['MA_Fast'] - df['MA_Slow']) / df['MA_Slow']) * 100

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

# Buy: PriceOsc crosses 0 + ST bullish
df['Buy'] = (df['PriceOsc'] > 0) & (df['PriceOsc'].shift(1) <= 0) & (df['ST_dir'] == 'up')
df['Sell'] = (df['PriceOsc'] < 0) & (df['PriceOsc'].shift(1) >= 0) & (df['ST_dir'] == 'down')

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

r = backtest('ST + PriceOsc')
print(f"\n=== ST + PriceOsc ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
