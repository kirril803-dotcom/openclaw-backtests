"""
Strategy: RSI Oversold Multiple Entry
Fixed: Use fractional shares to avoid margin issues
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['RSI'] = rsi(df['Close'])

class RsiStrategy(Strategy):
    def init(self):
        self.rsi = self.I(lambda: df['RSI'].values)
        self.bars_held = 0
        
    def next(self):
        if len(self.data) < 20:
            return
        
        rsi_val = self.rsi[-1]
        
        # Buy when RSI oversold
        if rsi_val < 35 and not self.position:
            # Use tiny fraction - 0.001 BTC
            self.buy(size=0.001)
            self.bars_held = 0
        
        # Sell when RSI normalized or after 3 bars
        elif self.position:
            self.bars_held += 1
            if rsi_val > 55 or self.bars_held >= 3:
                self.sell()
                self.bars_held = 0

bt = Backtest(df, RsiStrategy, cash=1_000_000, commission=0.001)
stats = bt.run()

print("=== RSI Strategy (Fixed) ===")
print(f"Return: {stats['Return [%]']:.2f}%")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Trades: {stats['# Trades']}")
if stats['# Trades'] > 0:
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    print(f"Sharpe: {stats['Sharpe Ratio']:.3f}")

import csv
with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'RSI Oversold (Fixed)',
        f"{stats['Return [%]']:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A', 'N/A', stats['# Trades']
    ])
