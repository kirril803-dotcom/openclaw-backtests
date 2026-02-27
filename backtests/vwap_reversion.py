"""
Strategy: VWAP Mean Reversion
Source: Custom - price reverts to VWAP

Logic:
- Buy when price is below VWAP by > 1%
- Sell when price is above VWAP by > 1%
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Calculate VWAP
df['TypicalPrice'] = (df['High'] + df['Low'] + df['Close']) / 3
df['VWAP'] = (df['TypicalPrice'] * df['Volume']).cumsum() / df['Volume'].cumsum()

class VwapReversion(Strategy):
    def init(self):
        self.close = self.I(lambda: df['Close'].values)
        self.vwap = self.I(lambda: df['VWAP'].values)
        
    def next(self):
        if len(self.data) < 10:
            return
        
        price = self.close[-1]
        vwap = self.vwap[-1]
        
        # Buy when price is 1% below VWAP
        if price < vwap * 0.99 and not self.position:
            self.buy(size=0.01)
        
        # Sell when price is 1% above VWAP
        elif price > vwap * 1.01 and self.position:
            self.sell()

# Run backtest
bt = Backtest(df, VwapReversion, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== VWAP Mean Reversion ===")
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
        'VWAP Mean Reversion',
        f"{stats['Return [%]']:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A', 'N/A', stats['# Trades']
    ])

print("\nResults saved!")
