"""
L1 Trend Swing - EMA 50/200 Crossover
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

# Fill NaN
df['EMA50'] = df['EMA50'].fillna(0)
df['EMA200'] = df['EMA200'].fillna(0)

# Trend: EMA50 > EMA200 = uptrend
df['Uptrend'] = df['EMA50'] > df['EMA200']
df['PrevUptrend'] = df['Uptrend'].shift(1).fillna(False)

# Signals: EMA50 crosses EMA200
df['LongSignal'] = (df['PrevUptrend'] == False) & (df['Uptrend'] == True)
df['ShortSignal'] = (df['PrevUptrend'] == True) & (df['Uptrend'] == False)

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(250, len(df)):
        price = df.iloc[i]['Close']
        
        if df.iloc[i]['LongSignal'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        
        elif df.iloc[i]['ShortSignal'] and pos == 'long':
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

r = backtest('L1 Trend Swing')
print(f"\n=== L1 Trend Swing ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
