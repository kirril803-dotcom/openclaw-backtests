"""
HispanoTrader GOAT - EMA 7/25 Backtest
Strategy: EMA crossover 7/25 with distance filter
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
print(f"Data: {len(df)} days")

# EMA
fastLen = 7
slowLen = 25

df['EMA_Fast'] = df['Close'].ewm(span=fastLen, adjust=False).mean()
df['EMA_Slow'] = df['Close'].ewm(span=slowLen, adjust=False).mean()

# Signals
df['Crossover'] = (df['EMA_Fast'] > df['EMA_Slow']) & (df['EMA_Fast'].shift(1) <= df['EMA_Slow'].shift(1))
df['Crossunder'] = (df['EMA_Fast'] < df['EMA_Slow']) & (df['EMA_Fast'].shift(1) >= df['EMA_Slow'].shift(1))

# Bull/Bear candles
df['BullCandle'] = df['Close'] > df['Open']
df['BearCandle'] = df['Close'] < df['Open']

# Filter by distance
df['EMA_Distance'] = abs(df['EMA_Fast'] - df['EMA_Slow'])

# Long: EMA cross up + distance > 0 + bull candle
df['LongSignal'] = df['Crossover'] & (df['EMA_Distance'] > 0) & df['BullCandle']
# Short: EMA cross down + distance > 0 + bear candle
df['ShortSignal'] = df['Crossunder'] & (df['EMA_Distance'] > 0) & df['BearCandle']

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        # Long entry
        if df.iloc[i]['LongSignal'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        # Exit: cross down
        elif df.iloc[i]['Crossunder'] and pos == 'long':
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

r = backtest('HispanoTrader GOAT EMA 7/25')
print(f"\n=== HispanoTrader GOAT ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
