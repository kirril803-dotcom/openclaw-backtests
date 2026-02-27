"""
Strategy: Supertrend V2 (Optimized)
Source: Custom - improved Supertrend with ATR multiplier

Logic:
- Supertrend = close - (ATR * multiplier)
- Buy when price crosses above Supertrend (bullish)
- Sell when price crosses below Supertrend (bearish)
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Calculate ATR
def atr(high, low, close, period=10):
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

df['ATR'] = atr(df['High'], df['Low'], df['Close'], 10)
df['Supertrend'] = df['Close'] - 3 * df['ATR']
df['PrevSupertrend'] = df['Supertrend'].shift(1)

class SupertrendV2(Strategy):
    def init(self):
        self.close = self.I(lambda: df['Close'].values)
        self.supertrend = self.I(lambda: df['Supertrend'].values)
        self.prev_st = self.I(lambda: df['PrevSupertrend'].values)
        
    def next(self):
        if len(self.data) < 20:
            return
        
        current_price = self.close[-1]
        prev_price = self.close[-2]
        current_st = self.supertrend[-1]
        prev_st = self.prev_st[-1]
        
        # Bullish crossover: price crosses above Supertrend
        if prev_price <= prev_st and current_price > current_st and not self.position:
            self.buy(size=0.01)
        
        # Bearish crossunder: price crosses below Supertrend
        elif prev_price >= prev_st and current_price < current_st and self.position:
            self.sell()

# Run backtest
bt = Backtest(df, SupertrendV2, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== Supertrend V2 ===")
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
        'Supertrend V2',
        f"{stats['Return [%]']:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A',
        'N/A',
        stats['# Trades']
    ])

print("\nResults saved!")
