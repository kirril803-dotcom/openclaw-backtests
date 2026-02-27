"""
Strategy: Stochastic RSI
Source: Custom - Stochastic applied to RSI for overbought/oversold

Logic:
- Buy when Stochastic RSI < 20 (oversold)
- Sell when Stochastic RSI > 80 (overbought)
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

# Calculate Stochastic RSI
def stoch_rsi(close, rsi_period=14, stoch_period=14, k_period=3, d_period=3):
    rsi_val = rsi(close, rsi_period)
    rsi_min = rsi_val.rolling(stoch_period).min()
    rsi_max = rsi_val.rolling(stoch_period).max()
    stoch_rsi = 100 * (rsi_val - rsi_min) / (rsi_max - rsi_min)
    return stoch_rsi

df['StochRSI'] = stoch_rsi(df['Close'])

class StochasticRSI(Strategy):
    def init(self):
        self.stoch = self.I(lambda: df['StochRSI'].values)
        self.bars_held = 0
        
    def next(self):
        if len(self.data) < 30:
            return
        
        stoch_val = self.stoch[-1]
        
        # Buy when oversold
        if stoch_val < 20 and not self.position:
            self.buy(size=0.01)
            self.bars_held = 0
        
        # Sell when overbought or after 5 bars
        elif self.position:
            self.bars_held += 1
            if stoch_val > 80 or self.bars_held >= 5:
                self.sell()
                self.bars_held = 0

# Run backtest
bt = Backtest(df, StochasticRSI, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== Stochastic RSI ===")
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
        'Stochastic RSI',
        f"{stats['Return [%]']:.2f}%",
        f"{stats['Max. Drawdown [%]']:.2f}%",
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else 'N/A',
        'N/A',
        'N/A',
        stats['# Trades']
    ])

print("\nResults saved!")
