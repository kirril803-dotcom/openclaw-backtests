"""
Strategy: RSI Mean Reversion
Source: Custom - simple RSI oversold/overbought reversal

Logic:
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought)
- Hold for at least 2 bars
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

df['RSI'] = rsi(df['Close'])

class RsiMeanReversion(Strategy):
    def init(self):
        self.rsi = self.I(lambda: df['RSI'].values)
        self.bars_held = 0
        
    def next(self):
        if len(self.data) < 20:
            return
        
        rsi_val = self.rsi[-1]
        
        # Buy when RSI oversold
        if rsi_val < 30 and not self.position:
            self.buy(size=0.1)
            self.bars_held = 0
        
        # Sell when RSI overbought or after holding for some time
        elif self.position:
            self.bars_held += 1
            if rsi_val > 70 or self.bars_held >= 5:
                self.sell()
                self.bars_held = 0

# Run backtest
bt = Backtest(df, RsiMeanReversion, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== RSI Mean Reversion ===")
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
        'RSI Mean Reversion',
        f"{stats['Return [%]']:.2f}",
        f"{stats['Max. Drawdown [%]']:.2f}",
        stats['# Trades'],
        f"{stats['Win Rate [%]']:.2f}" if stats['# Trades'] > 0 else '0',
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else '0'
    ])

print("\nResults saved!")
