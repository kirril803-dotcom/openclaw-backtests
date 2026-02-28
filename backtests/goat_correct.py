"""
HispanoTrader GOAT - CORRECT Backtest
EMA 7/25 crossover with candle filter
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# EMA
df['EMA7'] = df['Close'].ewm(span=7, adjust=False).mean()
df['EMA25'] = df['Close'].ewm(span=25, adjust=False).mean()

# Signals
# Long: EMA7 crosses above EMA25 + bullish candle (close > open)
# Short: EMA7 crosses below EMA25 + bearish candle (close < open)
df['EMA7_above'] = df['EMA7'] > df['EMA25']
df['EMA7_below'] = df['EMA7'] < df['EMA25']
df['EMA7_above_prev'] = df['EMA7_above'].shift(1)
df['EMA7_below_prev'] = df['EMA7_below'].shift(1)

# Crossover
df['Crossover_Long'] = df['EMA7_below_prev'] & df['EMA7_above']  # 7 crosses above 25
df['Crossover_Short'] = df['EMA7_above_prev'] & df['EMA7_below']  # 7 crosses below 25

# Bullish/Bearish candle filter
df['BullCandle'] = df['Close'] > df['Open']
df['BearCandle'] = df['Close'] < df['Open']

# Final signals
df['LongSignal'] = df['Crossover_Long'] & df['BullCandle']
df['ShortSignal'] = df['Crossover_Short'] & df['BearCandle']

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    wins = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        # Entry: Long
        if df.iloc[i]['LongSignal'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        
        # Exit: Short signal OR Friday close
        elif df.iloc[i]['ShortSignal'] and pos == 'long':
            cash = btc * price
            if price > df.iloc[i-1]['Close']:
                wins += 1
            pos = None
            btc = 0
    
    # Close at end
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    win_rate = wins / trades * 100 if trades > 0 else 0
    
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': win_rate}

r = backtest('HispanoTrader GOAT Correct')
print(f"\n=== HispanoTrader GOAT (CORRECT) ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
