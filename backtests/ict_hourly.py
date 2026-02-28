"""
ICT Silver Bullet Momentum - HOURLY Backtest
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
print(f"Data: {len(df)} hours")

# Hourly data - simulate strategy
# Bullish: 2 consecutive hourly closes up + volume increase
df['Bullish'] = df['Close'] > df['Open']
df['Bullish1'] = df['Bullish'].shift(1)
df['VolumeInc'] = df['Volume'] > df['Volume'].shift(1)

df['EntrySignal'] = df['Bullish'] & df['Bullish1'] & df['VolumeInc']

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        if df.iloc[i]['EntrySignal'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        elif pos == 'long':
            pnl = (price - df.iloc[i-1]['Close']) / df.iloc[i-1]['Close']
            if pnl >= 0.01:  # 1% target
                cash = btc * price
                wins += 1
                pos = None
                btc = 0
            elif pnl <= -0.005:  # -0.5% stop
                cash = btc * price
                pos = None
                btc = 0
    
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    win_rate = wins / trades * 100 if trades > 0 else 0
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': win_rate}

r = backtest('ICT Silver Bullet Hourly')
print(f"\n=== ICT Silver Bullet (Hourly) ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
