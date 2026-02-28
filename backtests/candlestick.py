"""
Reversal Candlestick Patterns
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Hammer / Inverted Hammer detection
df['Body'] = abs(df['Close'] - df['Open'])
df['Range'] = df['High'] - df['Low']
df['UpperWick'] = df['High'] - df[['Close', 'Open']].max(axis=1)
df['LowerWick'] = df[['Close', 'Open']].min(axis=1) - df['Low']

# Hammer: small body at top, long lower wick
df['Hammer'] = (df['LowerWick'] > 2 * df['Body']) & (df['UpperWick'] < df['Body']) & (df['Close'] > df['Open'])

# Engulfing
df['BullEngulf'] = (df['Close'] > df['Open']) & (df['Close'].shift(1) < df['Open'].shift(1)) & (df['Close'] > df['Open'].shift(1)) & (df['Open'] < df['Close'].shift(1))

# Trend filter
df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
df['Downtrend'] = df['Close'] < df['EMA20']

df['Buy'] = (df['Hammer'] | df['BullEngulf']) & df['Downtrend']
df['Sell'] = df['Close'] < df['Close'].shift(5)

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

r = backtest('Candlestick Reversal')
print(f"\n=== Candlestick Reversal ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
