"""
Strategy: MACD Divergence
Source: Custom - MACD histogram divergence from price

Logic:
- Buy when MACD histogram turns positive (crosses above 0)
- Sell when MACD histogram turns negative (crosses below 0)
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Calculate MACD
df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = df['EMA12'] - df['EMA26']
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['Hist'] = df['MACD'] - df['Signal']

class MacdDivergence(Strategy):
    def init(self):
        self.hist = self.I(lambda: df['Hist'].values)
        self.prev_hist = np.roll(self.hist, 1)
        
    def next(self):
        if len(self.data) < 30:
            return
        
        hist = self.hist[-1]
        prev_hist = self.prev_hist[-1]
        
        # Buy when histogram crosses above 0
        if prev_hist <= 0 and hist > 0 and not self.position:
            self.buy(size=0.01)
        
        # Sell when histogram crosses below 0
        elif prev_hist >= 0 and hist < 0 and self.position:
            self.sell()

# Run backtest
bt = Backtest(df, MacdDivergence, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== MACD Divergence ===")
print(f"Return: {stats['Return [%]']:.2f}%")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Trades: {stats['# Trades']}")
if stats['# Trades'] > 0:
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.3f}")

import csv
with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'MACD Divergence',
        f"{stats['Return [%]']:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A', 'N/A', stats['# Trades']
    ])

print("\nResults saved!")
