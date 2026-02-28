"""
Ichimoku + Supertrend
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Ichimoku
nine_period_high = df['High'].rolling(window=9).max()
nine_period_low = df['Low'].rolling(window=9).min()
df['Tenkan'] = (nine_period_high + nine_period_low) / 2

twentySix_period_high = df['High'].rolling(window=26).max()
twentySix_period_low = df['Low'].rolling(window=26).min()
df['Kijun'] = (twentySix_period_high + twentySix_period_low) / 2

df['SenkouA'] = ((df['Tenkan'] + df['Kijun']) / 2).shift(26)

fiftyTwo_period_high = df['High'].rolling(window=52).max()
fiftyTwo_period_low = df['Low'].rolling(window=52).min()
df['SenkouB'] = ((fiftyTwo_period_high + fiftyTwo_period_low) / 2).shift(26)

df['Chikou'] = df['Close'].shift(-26)

# ATR for Supertrend
period = 10
df['TR'] = np.maximum(df['High'] - df['Low'], 
                       np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                 abs(df['Low'] - df['Close'].shift(1))))
df['ATR'] = df['TR'].rolling(period).mean()

# Supertrend
multiplier = 3
df['Upper'] = (df['High'] + df['Low']) / 2 + multiplier * df['ATR']
df['Lower'] = (df['High'] + df['Low']) / 2 - multiplier * df['ATR']

df['ST_dir'] = 'up'
for i in range(1, len(df)):
    if df.iloc[i]['Close'] > df.iloc[i-1]['Upper']:
        df.loc[df.index[i], 'ST_dir'] = 'up'
    elif df.iloc[i]['Close'] < df.iloc[i-1]['Lower']:
        df.loc[df.index[i], 'ST_dir'] = 'down'
    else:
        df.loc[df.index[i], 'ST_dir'] = df.iloc[i-1]['ST_dir']

# Buy: Ichimoku bullish + ST bullish
df['Buy'] = (df['Close'] > df['SenkouA']) & (df['Close'] > df['SenkouB']) & (df['ST_dir'] == 'up') & (df['ST_dir'].shift(1) == 'down')
df['Sell'] = (df['ST_dir'] == 'down') & (df['ST_dir'].shift(1) == 'up')

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

r = backtest('Ichimoku + ST')
print(f"\n=== Ichimoku + ST ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
