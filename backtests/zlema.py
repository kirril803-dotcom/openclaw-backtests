"""
ZLEMA - Zero Lag EMA
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# ZLEMA
def zlema(series, period):
    lag = int((period - 1) / 2)
    ema_data = 2 * series - series.shift(lag)
    return ema_data.ewm(span=period, adjust=False).mean()

df['ZLEMA9'] = zlema(df['Close'], 9)
df['ZLEMA21'] = zlema(df['Close'], 21)

# Buy when ZLEMA9 crosses above ZLEMA21
df['Buy'] = (df['ZLEMA9'] > df['ZLEMA21']) & (df['ZLEMA9'].shift(1) <= df['ZLEMA21'].shift(1))
df['Sell'] = (df['ZLEMA9'] < df['ZLEMA21']) & (df['ZLEMA9'].shift(1) >= df['ZLEMA21'].shift(1))

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

r = backtest('ZLEMA')
print(f"\n=== ZLEMA ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
