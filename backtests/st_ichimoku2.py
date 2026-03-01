"""
Supertrend + Ichimoku
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Ichimoku
def ichimoku(df, period1=9, period2=26, period3=52):
    high9 = df['High'].rolling(period1).max()
    low9 = df['Low'].rolling(period1).min()
    df['Tenkan'] = (high9 + low9) / 2
    
    high26 = df['High'].rolling(period2).max()
    low26 = df['Low'].rolling(period2).min()
    df['Kijun'] = (high26 + low26) / 2
    
    df['SenkouA'] = ((df['Tenkan'] + df['Kijun']) / 2).shift(period2)
    
    high52 = df['High'].rolling(period3).max()
    low52 = df['Low'].rolling(period3).min()
    df['SenkouB'] = ((high52 + low52) / 2).shift(period2)
    
    df['Chikou'] = df['Close'].shift(-period2)

ichimoku(df)

# Supertrend
st_period = 10
df['TR'] = np.maximum(df['High'] - df['Low'],
                       np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                 abs(df['Low'] - df['Close'].shift(1))))
df['ATR'] = df['TR'].rolling(st_period).mean()
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

# Buy: Price above cloud + Tenkan > Kijun + ST bullish
df['Buy'] = (df['Close'] > df['SenkouA']) & (df['Close'] > df['SenkouB']) & (df['Tenkan'] > df['Kijun']) & (df['ST_dir'] == 'up')
df['Sell'] = (df['ST_dir'] == 'down') & (df['ST_dir'].shift(1) == 'up')

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    
    for i in range(100, len(df)):
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

r = backtest('ST + Ichimoku')
print(f"\n=== ST + Ichimoku ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
