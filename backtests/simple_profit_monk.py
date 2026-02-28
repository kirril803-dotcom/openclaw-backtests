"""
Simple Profit Monk - Backtest
Strategy: BB + ATR Trend Line crossover
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
print(f"Data: {len(df)} days")

# BB
BBperiod = 21
BBdeviations = 1.0

df['BB_Mid'] = df['Close'].rolling(BBperiod).mean()
df['BB_Std'] = df['Close'].rolling(BBperiod).std()
df['BB_Upper'] = df['BB_Mid'] + df['BB_Std'] * BBdeviations
df['BB_Lower'] = df['BB_Mid'] - df['BB_Std'] * BBdeviations

# ATR
df['ATR'] = df['Close'].diff().abs().rolling(5).mean()

# Trend Line
df['TrendLine'] = 0.0

for i in range(22, len(df)):
    bb_upper = df.iloc[i]['BB_Upper']
    bb_lower = df.iloc[i]['BB_Lower']
    close = df.iloc[i]['Close']
    low = df.iloc[i]['Low']
    high = df.iloc[i]['High']
    atr = df.iloc[i]['ATR']
    prev_trend = df.iloc[i-1]['TrendLine']
    
    if close > bb_upper:
        trend = low - atr
    elif close < bb_lower:
        trend = high + atr
    else:
        trend = prev_trend
    
    df.at[df.index[i], 'TrendLine'] = trend

# iTrend
df['iTrend'] = 0
for i in range(23, len(df)):
    if df.iloc[i]['TrendLine'] > df.iloc[i-1]['TrendLine']:
        df.at[df.index[i], 'iTrend'] = 1
    elif df.iloc[i]['TrendLine'] < df.iloc[i-1]['TrendLine']:
        df.at[df.index[i], 'iTrend'] = -1
    else:
        df.at[df.index[i], 'iTrend'] = df.iloc[i-1]['iTrend']

# Signals
df['Buy'] = (df['iTrend'].shift(1) == -1) & (df['iTrend'] == 1)
df['Sell'] = (df['iTrend'].shift(1) == 1) & (df['iTrend'] == -1)

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        if df.iloc[i]['Buy'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        elif df.iloc[i]['Sell'] and pos == 'long':
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

r = backtest('Simple Profit Monk')
print(f"\n=== Simple Profit Monk ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
