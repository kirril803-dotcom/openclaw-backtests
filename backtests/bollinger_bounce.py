"""
Bollinger Bands Bounce
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# Bollinger Bands
df['MA'] = df['Close'].rolling(20).mean()
df['STD'] = df['Close'].rolling(20).std()
df['Upper'] = df['MA'] + 2*df['STD']
df['Lower'] = df['MA'] - 2*df['STD']

# Buy when price touches lower band, sell when touches upper
df['Buy'] = df['Close'] <= df['Lower']
df['Sell'] = df['Close'] >= df['Upper']

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        if pos is None and df.iloc[i]['Buy']:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        elif pos == 'long' and df.iloc[i]['Sell']:
            cash = btc * price
            if cash > initial_cash * (1 + trades * 0.001):
                wins += 1
            pos = None
            btc = 0
    
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': wins/trades*100 if trades>0 else 0}

r = backtest('Bollinger Bands Bounce')
print(f"\n=== Bollinger Bands Bounce ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
