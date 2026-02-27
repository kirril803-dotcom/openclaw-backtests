"""
Strategy: RSI + MACD Combo
Source: Custom - combination of RSI oversold and MACD crossover

Logic:
- Buy when RSI < 30 (oversold) AND MACD crosses above signal
- Sell when RSI > 70 (overbought) OR MACD crosses below signal
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Calculate RSI
def rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Calculate MACD
def macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

df['RSI'] = rsi(df['Close'])
df['MACD'], df['Signal'], df['Hist'] = macd(df['Close'])

class RsiMacdCombo(Strategy):
    def init(self):
        self.rsi = self.I(lambda: df['RSI'].values)
        self.macd = self.I(lambda: df['MACD'].values)
        self.signal = self.I(lambda: df['Signal'].values)
        self.prev_macd = np.roll(self.macd, 1)
        self.prev_signal = np.roll(self.signal, 1)
        
    def next(self):
        if len(self.data) < 30:
            return
        
        rsi_val = self.rsi[-1]
        macd_val = self.macd[-1]
        signal_val = self.signal[-1]
        prev_macd = self.prev_macd[-1]
        prev_signal = self.prev_signal[-1]
        
        # MACD crossover (bullish)
        macd_bullish_cross = (prev_macd <= prev_signal) and (macd_val > signal_val)
        # MACD crossunder (bearish)
        macd_bearish_cross = (prev_macd >= prev_signal) and (macd_val < signal_val)
        
        # Buy: RSI oversold + MACD bullish cross
        if rsi_val < 35 and macd_bullish_cross and not self.position:
            self.buy(size=0.1)
        
        # Sell: RSI overbought OR MACD bearish cross
        elif (rsi_val > 65 or macd_bearish_cross) and self.position:
            self.sell()

# Run backtest
bt = Backtest(df, RsiMacdCombo, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== RSI + MACD Combo ===")
print(f"Return: {stats['Return [%]']:.2f}%")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Trades: {stats['# Trades']}")
if stats['# Trades'] > 0:
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.3f}")
    print(f"Best Trade: {stats['Best Trade [%]']:.2f}%")
    print(f"Worst Trade: {stats['Worst Trade [%]']:.2f}%")

# Save to results.csv
import csv
with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'RSI + MACD Combo',
        f"{stats['Return [%]']:.2f}",
        f"{stats['Max. Drawdown [%]']:.2f}",
        stats['# Trades'],
        f"{stats['Win Rate [%]']:.2f}" if stats['# Trades'] > 0 else '0',
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else '0'
    ])

print("\nResults saved!")
