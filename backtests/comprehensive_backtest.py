"""
Comprehensive Backtest with 5 years of BTC data
"""
import pandas as pd
import numpy as np

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
print(f"Data: {len(df)} days from {df.datetime.min()} to {df.datetime.max()}")

# Indicators
def rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    return 100 - (100 / (1 + gain / loss))

def ema(close, period):
    return close.ewm(span=period, adjust=False).mean()

def macd(close):
    ema12 = ema(close, 12)
    ema26 = ema(close, 26)
    return ema12 - ema26, ema(ema12 - ema26, 9)

df['RSI'] = rsi(df['Close'], 14)
df['EMA9'] = ema(df['Close'], 9)
df['EMA21'] = ema(df['Close'], 21)
df['EMA50'] = ema(df['Close'], 50)
df['EMA200'] = ema(df['Close'], 200)
df['MACD'], df['Signal'] = macd(df['Close'])
df['Hist'] = df['MACD'] - df['Signal']

def backtest(name, buy_cond, sell_cond, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    entry = 0
    trades = 0
    wins = 0
    losses = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        if buy_cond(df, i) and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            entry = price
            trades += 1
        elif sell_cond(df, i) and pos == 'long':
            cash = btc * price
            pnl = (price - entry) / entry * 100
            if pnl > 0:
                wins += 1
            else:
                losses += 1
            pos = None
            btc = 0
    
    final = cash if pos is None else btc * df.iloc[-1]['Close']
    roi = (final - initial_cash) / initial_cash * 100
    
    # Calculate drawdown
    equity = []
    c = initial_cash
    b = 0
    p = None
    e = 0
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        if buy_cond(df, i) and p is None:
            b = c / price
            c = 0
            p = 'long'
            e = price
        elif sell_cond(df, i) and p == 'long':
            c = b * price
            p = None
        val = c if p is None else b * price
        equity.append(val)
    
    max_eq = max(equity)
    dd = max([(max_eq - v) / max_eq * 100 for v in equity])
    
    return {
        'name': name,
        'roi': roi,
        'trades': trades,
        'wins': wins,
        'losses': losses,
        'win_rate': wins / trades * 100 if trades > 0 else 0,
        'max_dd': dd
    }

# Define strategies
strategies = [
    # RSI
    ('RSI Oversold', 
     lambda df, i: df.iloc[i]['RSI'] < 30,
     lambda df, i: df.iloc[i]['RSI'] > 70),
    
    # RSI + Trend
    ('RSI + Trend (EMA200)',
     lambda df, i: df.iloc[i]['RSI'] < 35 and df.iloc[i]['Close'] > df.iloc[i]['EMA200'],
     lambda df, i: df.iloc[i]['RSI'] > 65),
    
    # MACD Cross
    ('MACD Cross',
     lambda df, i: df.iloc[i]['Hist'] > 0 and df.iloc[i-1]['Hist'] <= 0,
     lambda df, i: df.iloc[i]['Hist'] < 0 and df.iloc[i-1]['Hist'] >= 0),
    
    # EMA Cross
    ('EMA Cross (9/21)',
     lambda df, i: df.iloc[i]['EMA9'] > df.iloc[i]['EMA21'] and df.iloc[i-1]['EMA9'] <= df.iloc[i-1]['EMA21'],
     lambda df, i: df.iloc[i]['EMA9'] < df.iloc[i]['EMA21'] and df.iloc[i-1]['EMA9'] >= df.iloc[i-1]['EMA21']),
    
    # EMA Cross + Trend
    ('EMA Cross + Trend',
     lambda df, i: df.iloc[i]['EMA9'] > df.iloc[i]['EMA21'] and df.iloc[i-1]['EMA9'] <= df.iloc[i-1]['EMA21'] and df.iloc[i]['Close'] > df.iloc[i]['EMA50'],
     lambda df, i: df.iloc[i]['EMA9'] < df.iloc[i]['EMA21']),
    
    # RSI + MACD Combo
    ('RSI + MACD',
     lambda df, i: df.iloc[i]['RSI'] < 40 and df.iloc[i]['Hist'] > 0,
     lambda df, i: df.iloc[i]['RSI'] > 60),
    
    # Golden Cross (50/200)
    ('Golden Cross (50/200)',
     lambda df, i: df.iloc[i]['EMA50'] > df.iloc[i]['EMA200'] and df.iloc[i-1]['EMA50'] <= df.iloc[i-1]['EMA200'],
     lambda df, i: df.iloc[i]['EMA50'] < df.iloc[i]['EMA200'] and df.iloc[i-1]['EMA50'] >= df.iloc[i-1]['EMA200']),
    
    # Mean Reversion
    ('Mean Reversion',
     lambda df, i: df.iloc[i]['Close'] < df.iloc[i]['EMA21'] * 0.95,
     lambda df, i: df.iloc[i]['Close'] > df.iloc[i]['EMA21']),
]

print("\n=== BACKTEST RESULTS (5 Years BTC) ===\n")
results = []
for name, buy, sell in strategies:
    r = backtest(name, buy, sell)
    results.append(r)
    print(f"{name}:")
    print(f"  ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}% | Max DD: {r['max_dd']:.2f}%")
    print()

# Save results
with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    for r in results:
        writer.writerow([r['name'], f"{r['roi']:.2f}%", f"{r['max_dd']:.2f}%", "N/A", "N/A", "N/A", r['trades']])

import csv
print("\nSaved to results.csv")
