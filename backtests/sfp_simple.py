"""
SFP (Swing Failure Pattern) - Simple version
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

lookback = 20

df['SwingHigh'] = df['High'].rolling(lookback).max().shift(1)
df['SwingLow'] = df['Low'].rolling(lookback).min().shift(1)

# SFP signals - simpler
df['SFP_Bull'] = (df['Low'] < df['SwingLow']) & (df['Close'] > df['SwingLow'])
df['SFP_Bear'] = (df['High'] > df['SwingHigh']) & (df['Close'] < df['SwingHigh'])

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        if df.iloc[i]['SFP_Bull'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        elif df.iloc[i]['SFP_Bear'] and pos == 'long':
            cash = btc * price
            if price > df.iloc[i-1]['Close']:
                wins += 1
            pos = None
            btc = 0
    
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    win_rate = wins / trades * 100 if trades > 0 else 0
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': win_rate}

r = backtest('SFP Simple')
print(f"\n=== SFP Simple ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
