"""
Strategy: EMA Crossover with Trend Filter
Source: Custom - Fast EMA crosses slow EMA, filtered by trend

Logic:
- Trend filter: price above 200 EMA = uptrend
- Buy when fast EMA crosses above slow EMA in uptrend
- Sell when fast EMA crosses below slow EMA
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Calculate EMAs
df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

class EmacrossoverTrend(Strategy):
    def init(self):
        self.ema9 = self.I(lambda: df['EMA9'].values)
        self.ema21 = self.I(lambda: df['EMA21'].values)
        self.ema200 = self.I(lambda: df['EMA200'].values)
        self.close = self.I(lambda: df['Close'].values)
        
    def next(self):
        if len(self.data) < 50:
            return
        
        ema9 = self.ema9[-1]
        ema21 = self.ema21[-1]
        ema200 = self.ema200[-1]
        close = self.close[-1]
        
        # Get previous values for crossover detection
        prev_ema9 = self.ema9[-2]
        prev_ema21 = self.ema21[-2]
        
        # Uptrend: price above 200 EMA
        in_uptrend = close > ema200
        
        # Bullish crossover: 9 EMA crosses above 21 EMA
        bullish_cross = (prev_ema9 <= prev_ema21) and (ema9 > ema21)
        
        # Bearish crossunder
        bearish_cross = (prev_ema9 >= prev_ema21) and (ema9 < ema21)
        
        # Buy in uptrend with bullish crossover
        if in_uptrend and bullish_cross and not self.position:
            self.buy(size=0.01)
        
        # Sell on bearish crossover or trend reversal
        elif bearish_cross and self.position:
            self.sell()
        elif not in_uptrend and self.position:
            self.sell()

# Run backtest
bt = Backtest(df, EmacrossoverTrend, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== EMA Crossover + Trend Filter ===")
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
        'EMA Crossover + Trend',
        f"{stats['Return [%]']:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A',
        'N/A',
        stats['# Trades']
    ])

print("\nResults saved!")
