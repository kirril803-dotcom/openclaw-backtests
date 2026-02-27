"""
Strategy: RSI with Normalized Data
Solution: Divide prices by 100 to avoid margin issues, multiply returns back
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Normalize: divide by 100 to get prices in 600-1200 range
SCALE = 100
df['Open'] = df['Open'] / SCALE
df['High'] = df['High'] / SCALE
df['Low'] = df['Low'] / SCALE
df['Close'] = df['Close'] / SCALE

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['RSI'] = rsi(df['Close'])

class RsiNormalized(Strategy):
    def init(self):
        self.rsi = self.I(lambda: df['RSI'].values)
        self.bars_held = 0
        
    def next(self):
        if len(self.data) < 20:
            return
        
        rsi_val = self.rsi[-1]
        
        # Buy when RSI oversold
        if rsi_val < 35 and not self.position:
            self.buy(size=0.1)  # 10% of normalized equity
            self.bars_held = 0
        
        # Sell when RSI normalized or after 3 bars
        elif self.position:
            self.bars_held += 1
            if rsi_val > 55 or self.bars_held >= 3:
                self.sell()
                self.bars_held = 0

bt = Backtest(df, RsiNormalized, cash=1_000_000, commission=0.001)
stats = bt.run()

# Multiply returns by SCALE to get real values
real_return = stats['Return [%]'] * SCALE

print("=== RSI Normalized ===")
print(f"Return: {real_return:.2f}% (scaled)")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Trades: {stats['# Trades']}")
if stats['# Trades'] > 0:
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    print(f"Sharpe: {stats['Sharpe Ratio']:.3f}")

import csv
with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'RSI Normalized',
        f"{real_return:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A', 'N/A', stats['# Trades']
    ])
