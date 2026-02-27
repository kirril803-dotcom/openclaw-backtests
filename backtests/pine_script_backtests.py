"""
Backtests from TradingView Pine Scripts - Parsed Indicators
SuperTrend (from AlgoFox) + One Percent A Week (from TASC)
"""
import pandas as pd
import numpy as np
import csv

# Load 5-year data
df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
print(f"Data: {len(df)} days")

# === INDICATORS FROM PINE SCRIPTS ===

def supertrend(high, low, close, period=10, multiplier=3):
    """SuperTrend indicator from Pine Script"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    
    upper = (high + low) / 2 + multiplier * atr
    lower = (high + low) / 2 - multiplier * atr
    
    direction = pd.Series(1, index=close.index)
    
    for i in range(1, len(close)):
        if close.iloc[i] > upper.iloc[i-1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lower.iloc[i-1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i-1]
            
        if direction.iloc[i] == 1:
            lower.iloc[i] = max(lower.iloc[i], lower.iloc[i-1])
        else:
            upper.iloc[i] = min(upper.iloc[i], upper.iloc[i-1])
    
    return upper, lower, direction

def ema(close, period):
    return close.ewm(span=period, adjust=False).mean()

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    return 100 - (100 / (1 + gain / loss))

# Calculate all indicators
df['EMA9'] = ema(df['Close'], 9)
df['EMA21'] = ema(df['Close'], 21)
df['EMA50'] = ema(df['Close'], 50)
df['EMA200'] = ema(df['Close'], 200)
df['RSI'] = rsi(df['Close'], 14)
df['Upper'], df['Lower'], df['ST_Direction'] = supertrend(df['High'], df['Low'], df['Close'], 10, 3)

# Day of week
df['DayOfWeek'] = df['datetime'].dt.dayofweek

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
    win_rate = wins / trades * 100 if trades > 0 else 0
    
    # Drawdown
    equity = []
    c = initial_cash
    b = 0
    p = None
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        if buy_cond(df, i) and p is None:
            b = c / price
            c = 0
            p = 'long'
        elif sell_cond(df, i) and p == 'long':
            c = b * price
            p = None
        val = c if p is None else b * price
        equity.append(val)
    
    max_eq = max(equity) if equity else initial_cash
    dd = max([(max_eq - v) / max_eq * 100 for v in equity]) if equity else 0
    
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': win_rate, 'max_dd': dd}

# === STRATEGIES FROM PINE SCRIPTS ===

strategies = [
    # 1. SUPERTREND (from AlgoFox Pine Script)
    ('SuperTrend (from Pine)',
     lambda df, i: df.iloc[i]['ST_Direction'] == 1,
     lambda df, i: df.iloc[i]['ST_Direction'] == -1),
    
    # 2. SUPERTREND + RSI FILTER
    ('SuperTrend + RSI Filter',
     lambda df, i: (df.iloc[i]['ST_Direction'] == 1) & (df.iloc[i]['RSI'] < 70),
     lambda df, i: df.iloc[i]['ST_Direction'] == -1),
    
    # 3. ONE PERCENT A WEEK (from TASC Pine Script)
    # Logic: Buy at 1% dip from Monday open, sell at 1% profit or Friday close
    ('One Percent A Week (TASC)',
     lambda df, i: df.iloc[i]['DayOfWeek'] == 0 and df.iloc[i]['Close'] < df.iloc[i]['Open'] * 0.99,
     lambda df, i: df.iloc[i]['DayOfWeek'] == 4),  # Sell on Friday
    
    # 4. EMA Cross (standard)
    ('EMA Cross 9/21',
     lambda df, i: df.iloc[i]['EMA9'] > df.iloc[i]['EMA21'] and df.iloc[i-1]['EMA9'] <= df.iloc[i-1]['EMA21'],
     lambda df, i: df.iloc[i]['EMA9'] < df.iloc[i]['EMA21']),
    
    # 5. SuperTrend + EMA Trend
    ('SuperTrend + EMA Trend',
     lambda df, i: (df.iloc[i]['ST_Direction'] == 1) & (df.iloc[i]['Close'] > df.iloc[i]['EMA50']),
     lambda df, i: df.iloc[i]['ST_Direction'] == -1),
    
    # 6. RSI Oversold
    ('RSI Oversold',
     lambda df, i: df.iloc[i]['RSI'] < 30,
     lambda df, i: df.iloc[i]['RSI'] > 70),
    
    # 7. RSI + EMA Trend
    ('RSI + EMA Trend',
     lambda df, i: (df.iloc[i]['RSI'] < 35) & (df.iloc[i]['Close'] > df.iloc[i]['EMA200']),
     lambda df, i: df.iloc[i]['RSI'] > 65),
    
    # 8. Golden Cross
    ('Golden Cross 50/200',
     lambda df, i: (df.iloc[i]['EMA50'] > df.iloc[i]['EMA200']) & (df.iloc[i-1]['EMA50'] <= df.iloc[i-1]['EMA200']),
     lambda df, i: (df.iloc[i]['EMA50'] < df.iloc[i]['EMA200']) & (df.iloc[i-1]['EMA50'] >= df.iloc[i-1]['EMA200'])),
]

print("\n=== BACKTESTS FROM TRADINGVIEW PINE SCRIPTS ===\n")
results = []
for name, buy, sell in strategies:
    r = backtest(name, buy, sell)
    results.append(r)
    print(f"{r['name']}:")
    print(f"  ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}% | Max DD: {r['max_dd']:.2f}%")
    print()

# Save to CSV
with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    for r in results:
        writer.writerow([r['name'], f"{r['roi']:.2f}%", f"{r['max_dd']:.2f}%", "N/A", "N/A", "N/A", r['trades']])

print("\n=== PARSED INDICATORS FROM PINE SCRIPTS ===")
print("1. SuperTrend (AlgoFox) - ATR-based trend indicator")
print("2. EMA (Exponential Moving Average) - 9, 21, 50, 200 periods")
print("3. RSI (Relative Strength Index)")
print("4. DayOfWeek (for One Percent A Week strategy)")
print("\nSaved to results.csv")
