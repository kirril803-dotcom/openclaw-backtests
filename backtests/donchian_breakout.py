"""
Strategy: Donchian Channel Breakout (Fixed)
Source: Classic - price breaks out of channel highs
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Calculate Donchian Channel
df['High20'] = df['High'].rolling(20).max()
df['Low20'] = df['Low'].rolling(20).min()
df['PrevHigh20'] = df['High20'].shift(1)

class DonchianBreakout(Strategy):
    def init(self):
        self.high = self.I(lambda: df['High'].values)
        self.low = self.I(lambda: df['Low'].values)
        self.prev_high20 = self.I(lambda: df['PrevHigh20'].values)
        self.entry_bar = 0
        
    def next(self):
        if len(self.data) < 25:
            return
        
        current_high = self.high[-1]
        current_low = self.low[-1]
        prev_channel = self.prev_high20[-1]
        
        # Buy: high breaks above previous channel high
        if current_high > prev_channel and not self.position:
            self.buy(size=0.01)
            self.entry_bar = len(self.data)
        
        # Sell: position open for 3+ bars
        elif self.position:
            if len(self.data) - self.entry_bar >= 3:
                self.sell()

# Run backtest
bt = Backtest(df, DonchianBreakout, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== Donchian Channel Breakout ===")
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
        'Donchian Breakout v2',
        f"{stats['Return [%]']:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A',
        'N/A',
        stats['# Trades']
    ])

print("\nResults saved!")
