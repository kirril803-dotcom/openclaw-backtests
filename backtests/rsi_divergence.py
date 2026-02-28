"""
RSI Divergence Strategy - Fixed
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# RSI
delta = df['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

# Simple RSI reversal: buy <30, sell >70 or after X bars
df['Buy'] = df['RSI'] < 30
df['Sell'] = df['RSI'] > 70

def backtest(name, initial_cash=10000, exit_bars=5):
    cash = initial_cash
    btc = 0
    pos = None
    entry_bar = 0
    trades = 0
    wins = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        if pos is None and df.iloc[i]['Buy']:
            btc = cash / price
            cash = 0
            pos = 'long'
            entry_bar = i
            trades += 1
        elif pos == 'long':
            # Exit conditions
            if df.iloc[i]['Sell'] or (i - entry_bar >= exit_bars):
                pnl = price - df.iloc[entry_bar]['Close']
                cash = btc * price
                if pnl > 0:
                    wins += 1
                pos = None
                btc = 0
    
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': wins/trades*100 if trades>0 else 0}

r = backtest('RSI Divergence')
print(f"\n=== RSI Divergence ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
