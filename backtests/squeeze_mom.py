"""
Squeeze Momentum
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Bollinger Bands
period = 20
mult = 2
df['BB_MA'] = df['Close'].rolling(period).mean()
df['BB_STD'] = df['Close'].rolling(period).std()
df['BB_Upper'] = df['BB_MA'] + mult * df['BB_STD']
df['BB_Lower'] = df['BB_MA'] - mult * df['BB_STD']

# Keltner Channel
df['TR'] = np.maximum(df['High'] - df['Low'],
                       np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                 abs(df['Low'] - df['Close'].shift(1))))
df['ATR'] = df['TR'].rolling(period).mean()
df['KC_Upper'] = df['BB_MA'] + 1.5 * df['ATR']
df['KC_Lower'] = df['BB_MA'] - 1.5 * df['ATR']

# Squeeze: BB inside KC
df['Squeeze'] = (df['BB_Lower'] > df['KC_Lower']) & (df['BB_Upper'] < df['KC_Upper'])

# Momentum
df['Mom'] = df['Close'] - df['Close'].rolling(20).mean()

# Buy when squeeze releases and momentum is positive
df['Buy'] = (df['Squeeze'].shift(1) == True) & (df['Squeeze'] == False) & (df['Mom'] > 0)
df['Sell'] = (df['Squeeze'].shift(1) == True) & (df['Squeeze'] == False) & (df['Mom'] < 0)

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

r = backtest('Squeeze Momentum')
print(f"\n=== Squeeze Momentum ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
