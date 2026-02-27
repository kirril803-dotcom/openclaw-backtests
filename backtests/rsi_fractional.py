"""
Using FractionalBacktest for BTC
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import FractionalBacktest

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def rsi(close, period=7):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['RSI'] = rsi(df['Close'], 7)

class RsiStrategy(Strategy):
    def init(self):
        self.rsi = self.I(lambda: df['RSI'].values)
        
    def next(self):
        if len(self.data) < 10:
            return
        
        rsi_val = self.rsi[-1]
        
        if rsi_val < 40 and not self.position:
            self.buy()
        
        elif self.position and rsi_val > 60:
            self.sell()

# Use FractionalBacktest
bt = FractionalBacktest(df, RsiStrategy, cash=10000, commission=0.001)
stats = bt.run()

print("=== RSI Fractional ===")
print(f"Return: {stats['Return [%]']:.2f}%")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Trades: {stats['# Trades']}")
if stats['# Trades'] > 0:
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    print(f"Sharpe: {stats['Sharpe Ratio']:.3f}")
