"""
Supertrend + ADX
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# ADX
period = 14
df['TR'] = np.maximum(df['High'] - df['Low'],
                       np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                 abs(df['Low'] - df['Close'].shift(1))))
df['+DM'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
                       np.maximum(df['High'] - df['High'].shift(1), 0), 0)
df['-DM'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
                       np.maximum(df['Low'].shift(1) - df['Low'], 0), 0)

df['+DI'] = 100 * df['+DM'].rolling(period).mean() / df['TR'].rolling(period).mean()
df['-DI'] = 100 * df['-DM'].rolling(period).mean() / df['TR'].rolling(period).mean()
df['DX'] = 100 * abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])
df['ADX'] = df['DX'].rolling(period).mean()

# ATR for Supertrend
st_period = 10
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

# Buy: ADX > 20 + DI+ > DI- + ST bullish
df['Buy'] = (df['ADX'] > 20) & (df['+DI'] > df['-DI']) & (df['ST_dir'] == 'up') & (df['ST_dir'].shift(1) == 'down')
df['Sell'] = (df['ADX'] > 20) & (df['+DI'] < df['-DI']) & (df['ST_dir'] == 'down') & (df['ST_dir'].shift(1) == 'up')

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

r = backtest('ST + ADX')
print(f"\n=== ST + ADX ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
