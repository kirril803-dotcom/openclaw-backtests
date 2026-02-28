"""
ADX Dynamic Zone Inside SuperTrend - Backtest
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
print(f"Data: {len(df)} days")

# Indicators
def supertrend(high, low, close, period=5, multiplier=3):
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    upper = (high + low) / 2 + multiplier * atr
    lower = (high + low) / 2 - multiplier * atr
    return upper, lower

def adx(high, low, close, period=20):
    up = high.diff()
    down = -low.diff()
    plus_dm = up.where((up > down) & (up > 0), 0)
    minus_dm = down.where((down > up) & (down > 0), 0)
    tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
    plus = 100 * plus_dm.rolling(period).mean() / tr.rolling(period).mean()
    minus = 100 * minus_dm.rolling(period).mean() / tr.rolling(period).mean()
    adx = 100 * (plus - minus).abs() / (plus + minus)
    return adx

df['Upper'], df['Lower'] = supertrend(df['High'], df['Low'], df['Close'])
df['ADX'] = adx(df['High'], df['Low'], df['Close'])

# Support/Resistance
df['Support'] = df['Low'].rolling(33).min()
df['Resistance'] = df['High'].rolling(17).max()

# Entry signals
df['EntryLong'] = (df['Close'] < df['Lower']) & (df['Close'] >= df['Support'])
df['EntryShort'] = (df['Close'] > df['Upper']) & (df['Close'] <= df['Resistance'])

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    entry = 0
    trades = 0
    wins = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        
        if df.iloc[i]['EntryLong'] and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            entry = price
            trades += 1
        elif pos == 'long':
            pnl = (price - entry) / entry * 100
            if pnl >= 1.5 or pnl <= -2:
                cash = btc * price
                if pnl > 0:
                    wins += 1
                pos = None
                btc = 0
    
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    win_rate = wins / trades * 100 if trades > 0 else 0
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': win_rate}

r = backtest('ADX Dynamic Zone SuperTrend')
print(f"\n=== ADX Dynamic Zone SuperTrend ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
