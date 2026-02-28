"""
Trend Intensity Index
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# SMA
df['SMA'] = df['Close'].rolling(30).mean()

# Count bars above SMA
def count_above(series, period):
    result = []
    for i in range(len(series)):
        if i < period - 1:
            result.append(np.nan)
        else:
            count = (series.iloc[i-period+1:i+1] > series.rolling(period).mean().iloc[i]).sum()
            result.append(count / period * 100)
    return pd.Series(result, index=series.index)

df['TII'] = count_above(df['Close'], 30)

# Buy when TII < 20 (oversold trend), sell when TII > 80
df['Buy'] = (df['TII'] < 20) & (df['TII'].shift(1) >= 20)
df['Sell'] = (df['TII'] > 80) & (df['TII'].shift(1) <= 80)

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

r = backtest('Trend Intensity')
print(f"\n=== Trend Intensity ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
