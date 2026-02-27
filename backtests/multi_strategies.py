"""
Multiple Strategies with Custom Backtester
"""
import pandas as pd
import numpy as np

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'])
df.columns = ['datetime', 'Open', 'High', 'Low', 'Close', 'Volume']

# Indicators
def rsi(close, period=7):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    return 100 - (100 / (1 + gain / loss))

def ema(close, period):
    return close.ewm(span=period, adjust=False).mean()

def macd(close):
    ema12 = ema(close, 12)
    ema26 = ema(close, 26)
    macd_line = ema12 - ema26
    signal = ema(macd_line, 9)
    return macd_line, signal

df['RSI'] = rsi(df['Close'], 7)
df['EMA9'] = ema(df['Close'], 9)
df['EMA21'] = ema(df['Close'], 21)
df['MACD'], df['Signal'] = macd(df['Close'])
df['Hist'] = df['MACD'] - df['Signal']

def backtest_strategies():
    results = []
    
    # 1. RSI Strategy
    cash = 10000
    btc = 0
    pos = None
    entry = 0
    trades = 0
    
    for i in range(20, len(df)):
        rsi_v = df.iloc[i]['RSI']
        price = df.iloc[i]['Close']
        
        if rsi_v < 40 and pos is None:
            btc = cash / price
            pos = 'long'
            entry = price
            cash = 0
            trades += 1
        elif pos == 'long' and rsi_v > 60:
            cash = btc * price
            pos = None
    
    final = cash if pos is None else btc * df.iloc[-1]['Close']
    roi = (final - 10000) / 10000 * 100
    results.append(('RSI', roi, trades))
    
    # 2. MACD Crossover
    cash = 10000
    btc = 0
    pos = None
    entry = 0
    trades = 0
    
    for i in range(30, len(df)):
        macd_v = df.iloc[i]['MACD']
        signal_v = df.iloc[i]['Signal']
        prev_macd = df.iloc[i-1]['MACD']
        prev_signal = df.iloc[i-1]['Signal']
        price = df.iloc[i]['Close']
        
        # Bullish cross
        if prev_macd <= prev_signal and macd_v > signal_v and pos is None:
            btc = cash / price
            pos = 'long'
            entry = price
            cash = 0
            trades += 1
        # Bearish cross
        elif prev_macd >= prev_signal and macd_v < signal_v and pos == 'long':
            cash = btc * price
            pos = None
    
    final = cash if pos is None else btc * df.iloc[-1]['Close']
    roi = (final - 10000) / 10000 * 100
    results.append(('MACD Crossover', roi, trades))
    
    # 3. EMA Cross
    cash = 10000
    btc = 0
    pos = None
    trades = 0
    
    for i in range(30, len(df)):
        ema9 = df.iloc[i]['EMA9']
        ema21 = df.iloc[i]['EMA21']
        prev_ema9 = df.iloc[i-1]['EMA9']
        prev_ema21 = df.iloc[i-1]['EMA21']
        price = df.iloc[i]['Close']
        
        if prev_ema9 <= prev_ema21 and ema9 > ema21 and pos is None:
            btc = cash / price
            pos = 'long'
            cash = 0
            trades += 1
        elif prev_ema9 >= prev_ema21 and ema9 < ema21 and pos == 'long':
            cash = btc * price
            pos = None
    
    final = cash if pos is None else btc * df.iloc[-1]['Close']
    roi = (final - 10000) / 10000 * 100
    results.append(('EMA Cross', roi, trades))
    
    # 4. RSI + MACD Combo
    cash = 10000
    btc = 0
    pos = None
    trades = 0
    
    for i in range(30, len(df)):
        rsi_v = df.iloc[i]['RSI']
        macd_v = df.iloc[i]['MACD']
        signal_v = df.iloc[i]['Signal']
        prev_macd = df.iloc[i-1]['MACD']
        prev_signal = df.iloc[i-1]['Signal']
        price = df.iloc[i]['Close']
        
        macd_bullish = prev_macd <= prev_signal and macd_v > signal_v
        
        if rsi_v < 45 and macd_bullish and pos is None:
            btc = cash / price
            pos = 'long'
            cash = 0
            trades += 1
        elif pos == 'long' and rsi_v > 65:
            cash = btc * price
            pos = None
    
    final = cash if pos is None else btc * df.iloc[-1]['Close']
    roi = (final - 10000) / 10000 * 100
    results.append(('RSI+MACD', roi, trades))
    
    # 5. Histogram Reversal
    cash = 10000
    btc = 0
    pos = None
    trades = 0
    
    for i in range(30, len(df)):
        hist = df.iloc[i]['Hist']
        prev_hist = df.iloc[i-1]['Hist']
        price = df.iloc[i]['Close']
        
        # Hist crosses above 0
        if prev_hist <= 0 and hist > 0 and pos is None:
            btc = cash / price
            pos = 'long'
            cash = 0
            trades += 1
        # Hist crosses below 0
        elif prev_hist >= 0 and hist < 0 and pos == 'long':
            cash = btc * price
            pos = None
    
    final = cash if pos is None else btc * df.iloc[-1]['Close']
    roi = (final - 10000) / 10000 * 100
    results.append(('MACD Hist', roi, trades))
    
    return results

results = backtest_strategies()

print("=== MULTIPLE STRATEGIES ===")
for name, roi, trades in results:
    print(f"{name}: ROI={roi:.2f}%, Trades={trades}")

# Save to CSV
import csv
with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    for name, roi, trades in results:
        writer.writerow([name, f"{roi:.2f}%", "N/A", "N/A", "N/A", "N/A", trades])

print("\nSaved to results.csv")
