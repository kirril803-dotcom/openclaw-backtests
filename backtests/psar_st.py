"""
Parabolic SAR + Supertrend
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Parabolic SAR
af = 0.02
af_max = 0.2
df['PSAR'] = df['Close'].copy()
df['PSAR_dir'] = 'up'

for i in range(1, len(df)):
    prev_psar = df.iloc[i-1]['PSAR']
    prev_af = df.iloc[i-1].get('AF', af)
    prev_ep = df.iloc[i-1].get('EP', df.iloc[i-1]['High'])
    
    if df.iloc[i-1]['PSAR_dir'] == 'up':
        psar = prev_psar + prev_af * (prev_ep - prev_psar)
        if df.iloc[i]['Low'] < psar:
            df.loc[df.index[i], 'PSAR_dir'] = 'down'
            df.loc[df.index[i], 'PSAR'] = prev_ep
            df.loc[df.index[i], 'EP'] = df.iloc[i]['Low']
            df.loc[df.index[i], 'AF'] = af
        else:
            df.loc[df.index[i], 'PSAR'] = psar
            df.loc[df.index[i], 'PSAR_dir'] = 'up'
            if df.iloc[i]['High'] > prev_ep:
                df.loc[df.index[i], 'EP'] = df.iloc[i]['High']
                df.loc[df.index[i], 'AF'] = min(prev_af + af, af_max)
            else:
                df.loc[df.index[i], 'EP'] = prev_ep
                df.loc[df.index[i], 'AF'] = prev_af
    else:
        psar = prev_psar - prev_af * (prev_psar - prev_ep)
        if df.iloc[i]['High'] > psar:
            df.loc[df.index[i], 'PSAR_dir'] = 'up'
            df.loc[df.index[i], 'PSAR'] = prev_ep
            df.loc[df.index[i], 'EP'] = df.iloc[i]['High']
            df.loc[df.index[i], 'AF'] = af
        else:
            df.loc[df.index[i], 'PSAR'] = psar
            df.loc[df.index[i], 'PSAR_dir'] = 'down'
            if df.iloc[i]['Low'] < prev_ep:
                df.loc[df.index[i], 'EP'] = df.iloc[i]['Low']
                df.loc[df.index[i], 'AF'] = min(prev_af + af, af_max)
            else:
                df.loc[df.index[i], 'EP'] = prev_ep
                df.loc[df.index[i], 'AF'] = prev_af

# ATR for Supertrend
st_period = 10
df['TR'] = np.maximum(df['High'] - df['Low'], 
                       np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                 abs(df['Low'] - df['Close'].shift(1))))
df['ATR2'] = df['TR'].rolling(st_period).mean()

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

# Buy: PSAR flips to up + ST bullish
df['Buy'] = (df['PSAR_dir'] == 'up') & (df['PSAR_dir'].shift(1) == 'down') & (df['ST_dir'] == 'up')
df['Sell'] = (df['PSAR_dir'] == 'down') & (df['PSAR_dir'].shift(1) == 'up') & (df['ST_dir'] == 'down')

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

r = backtest('PSAR + ST')
print(f"\n=== PSAR + ST ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
