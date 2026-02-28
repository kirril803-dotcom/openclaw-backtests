"""
Ichimoku Cloud
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

twenty_six_period_high = df['High'].rolling(window=26).max()
twenty_six_period_low = df['Low'].rolling(window=26).min()
df['Kijun'] = (twenty_six_period_high + twenty_six_period_low) / 2

df['SenkouA'] = ((df['Tenkan'] + df['Kijun']) / 2).shift(26)

df['SenkouB'] = ((df['High'].rolling(window=52).max() + df['Low'].rolling(window=52).min()) / 2).shift(26)

df['Chikou'] = df['Close'].shift(-26)

# Buy: Tenkan crosses above Kijun
df['Buy'] = (df['Tenkan'] > df['Kijun']) & (df['Tenkan'].shift(1) <= df['Kijun'].shift(1))
df['Sell'] = (df['Tenkan'] < df['Kijun']) & (df['Tenkan'].shift(1) >= df['Kijun'].shift(1))

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

r = backtest('Ichimoku')
print(f"\n=== Ichimoku ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
