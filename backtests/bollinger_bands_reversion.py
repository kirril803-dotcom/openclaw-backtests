"""
Strategy: Bollinger Bands Mean Reversion
Source: Custom - price reverts to Bollinger bands middle

Logic:
- Buy when price touches lower Bollinger band
- Sell when price touches upper Bollinger band
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Calculate Bollinger Bands
df['BB_Middle'] = df['Close'].rolling(20).mean()
df['BB_Std'] = df['Close'].rolling(20).std()
df['BB_Upper'] = df['BB_Middle'] + 2 * df['BB_Std']
df['BB_Lower'] = df['BB_Middle'] - 2 * df['BB_Std']

class BollingerBandsRev(Strategy):
    def init(self):
        self.close = self.I(lambda: df['Close'].values)
        self.bb_upper = self.I(lambda: df['BB_Upper'].values)
        self.bb_lower = self.I(lambda: df['BB_Lower'].values)
        
    def next(self):
        if len(self.data) < 25:
            return
        
        price = self.close[-1]
        upper = self.bb_upper[-1]
        lower = self.bb_lower[-1]
        
        # Buy at lower band
        if price <= lower and not self.position:
            self.buy(size=0.01)
        
        # Sell at upper band or after 3 bars
        elif self.position:
            if price >= upper:
                self.sell()

# Run backtest
bt = Backtest(df, BollingerBandsRev, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== Bollinger Bands Mean Reversion ===")
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
        'Bollinger Bands Reversion',
        f"{stats['Return [%]']:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A',
        'N/A',
        stats['# Trades']
    ])

print("\nResults saved!")
