"""
[blackcat] L1 Dynamic Defense Line - Backtest
Strategy: Stochastic-like oscillator with EMA crossover
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
print(f"Data: {len(df)} days")

# Calculate Defense Line
# Based on: Stochastic position + EMA
period = 34
lowest34 = df['Low'].rolling(period).min()
highest34 = df['High'].rolling(period).max()

typical_price = (2 * df['Close'] + df['High'] + df['Low']) / 4
stochastic = (typical_price - lowest34) / (highest34 - lowest34) * 100
stochastic = stochastic.fillna(50)

# Defense Line B = 8-period EMA of stochastic
defense_line_b = stochastic.ewm(span=8).mean()
# Defense Line B1 = 5-period EMA
defense_line_b1 = defense_line_b.ewm(span=5).mean()

# Buy/Sell Diff
buy_sell_diff = defense_line_b - defense_line_b1
prev_diff = buy_sell_diff.shift(1)

# Signals
buy_signal = (prev_diff < 0) & (buy_sell_diff > 0)
sell_signal = (prev_diff > 0) & (buy_sell_diff < 0)

df['BuySignal'] = buy_signal
df['SellSignal'] = sell_signal

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

r = backtest('Blackcat L1 Defense')
print(f"\n=== Blackcat L1 Defense ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
