"""
Strategy: ATR Trailing Stop
Source: Custom - ATR-based trailing stop strategy

Logic:
- Buy when price crosses above ATR-based stop
- Sell when price crosses below ATR-based stop
- Uses ATR for volatility-adjusted stops
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Calculate ATR
def atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

df['ATR'] = atr(df['High'], df['Low'], df['Close'])

# Calculate ATR-based stop (2.5 ATR from close)
df['LongStop'] = df['Close'] - 2.5 * df['ATR']
df['ShortStop'] = df['Close'] + 2.5 * df['ATR']

class AtrTrailingStop(Strategy):
    def init(self):
        self.atr = self.I(lambda: df['ATR'].values)
        self.close = self.I(lambda: df['Close'].values)
        self.long_stop = self.I(lambda: df['LongStop'].values)
        self.prev_close = np.roll(self.close, 1)
        
    def next(self):
        if len(self.data) < 20:
            return
        
        current_price = self.close[-1]
        prev_price = self.prev_close[-1]
        long_stop = self.long_stop[-1]
        
        # Buy when price crosses above long stop (breakout)
        if prev_price < long_stop and current_price > long_stop and not self.position:
            self.buy(size=0.1)
        
        # Sell when price falls below stop
        elif current_price < long_stop and self.position:
            self.sell()

# Run backtest
bt = Backtest(df, AtrTrailingStop, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== ATR Trailing Stop ===")
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
        'ATR Trailing Stop',
        f"{stats['Return [%]']:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A',
        'N/A',
        stats['# Trades']
    ])

print("\nResults saved!")
