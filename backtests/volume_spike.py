"""
Volume-based strategy - Simple version
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
print(f"Data: {len(df)} days")

# Volume spike + price action
df['VolSMA'] = df['Volume'].rolling(20).mean()
df['VolSpike'] = df['Volume'] > df['VolSMA'] * 1.5

# Buy: volume spike + price up
df['BuySignal'] = df['VolSpike'] & (df['Close'] > df['Open'])
# Sell: volume spike + price down
df['SellSignal'] = df['VolSpike'] & (df['Close'] < df['Open'])

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        if df.iloc[i]['BuySignal'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        elif df.iloc[i]['SellSignal'] and pos == 'long':
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

r = backtest('Volume Spike')
print(f"\n=== Volume Spike ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
