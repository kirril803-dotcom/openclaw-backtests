"""
algov2 - EMA 50/2 Breakout with Fixed TP
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# EMA 50 high/low and EMA 2
df['EMA50_H'] = df['High'].rolling(50).mean()
df['EMA50_L'] = df['Low'].rolling(50).mean()
df['EMA2'] = df['Close'].ewm(span=2, adjust=False).mean()

# Signals
df['Buy_Signal'] = (df['EMA2'] > df['EMA50_H']) & (df['Close'] > df['EMA50_H']) & \
                   ((df['EMA2'].shift(1) <= df['EMA50_H'].shift(1)) | (df['Close'].shift(1) <= df['EMA50_H'].shift(1)))

df['Sell_Signal'] = (df['EMA2'] < df['EMA50_L']) & (df['Close'] < df['EMA50_L']) & \
                    ((df['EMA2'].shift(1) >= df['EMA50_L'].shift(1)) | (df['Close'].shift(1) >= df['EMA50_L'].shift(1)))

# Fixed TP: 1% (more realistic for BTC hourly)
TP_PCT = 0.01

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    tp_price = None
    trades = 0
    wins = 0
    
    for i in range(100, len(df)):
        price = df.iloc[i]['Close']
        
        if pos is None:
            # Entry
            if df.iloc[i]['Buy_Signal']:
                btc = cash / price
                cash = 0
                pos = 'long'
                tp_price = price * (1 + TP_PCT)
                trades += 1
            elif df.iloc[i]['Sell_Signal']:
                # Short (simplified - just track long for now)
                pass
        
        elif pos == 'long':
            # Check TP
            if price >= tp_price:
                cash = btc * tp_price
                wins += 1
                pos = None
                btc = 0
                tp_price = None
            # Also exit on sell signal
            elif df.iloc[i]['Sell_Signal']:
                cash = btc * price
                pos = None
                btc = 0
                tp_price = None
    
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    win_rate = wins / trades * 100 if trades > 0 else 0
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': win_rate}

r = backtest('AlgoV2 EMA 50/2')
print(f"\n=== AlgoV2 ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
