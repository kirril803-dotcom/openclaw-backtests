"""
Hull MA Cross
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Hull Moving Average
def hma(series, period):
    half_length = int(period / 2)
    sqrt_length = int(np.sqrt(period))
    wmaf = series.rolling(half_length).apply(lambda x: np.sum(x * np.arange(1, half_length + 1)) / np.sum(np.arange(1, half_length + 1)), raw=True)
    wmas = series.rolling(period).apply(lambda x: np.sum(x * np.arange(1, period + 1)) / np.sum(np.arange(1, period + 1)), raw=True)
    diff = 2 * wmaf - wmas
    return diff.rolling(sqrt_length).apply(lambda x: np.sum(x * np.arange(1, sqrt_length + 1)) / np.sum(np.arange(1, sqrt_length + 1)), raw=True)

df['HMA9'] = hma(df['Close'], 9)
df['HMA21'] = hma(df['Close'], 21)

# Buy: HMA9 crosses above HMA21
df['Buy'] = (df['HMA9'] > df['HMA21']) & (df['HMA9'].shift(1) <= df['HMA21'].shift(1))
df['Sell'] = (df['HMA9'] < df['HMA21']) & (df['HMA9'].shift(1) >= df['HMA21'].shift(1))

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

r = backtest('Hull MA')
print(f"\n=== Hull MA ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
