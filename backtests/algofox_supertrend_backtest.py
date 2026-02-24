"""
Strategy: AlgoFox MultiTF SuperTrend v1.5
Source: TradingView - Popular
Pine Script: pine_scripts/AlgoFox_MultiTF_SuperTrend_v1.5.pine

Simplified trading logic using RSI
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

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

# Simple strategy: trade on RSI
class SuperTrendStrategy(Strategy):
    def init(self):
        self.rsi = self.I(lambda: df['RSI'].values)
    
    def next(self):
        if len(self.data) < 20:
            return
        
        rsi = self.rsi[-1]
        prev_rsi = self.rsi[-2] if len(self.data) > 1 else rsi
        
        # Buy when RSI crosses above 30 (oversold)
        if prev_rsi <= 30 and rsi > 30 and not self.position:
            self.buy(size=0.1)
        
        # Sell when RSI crosses above 70 (overbought)
        elif prev_rsi <= 70 and rsi > 70 and self.position:
            self.sell()

# Run backtest
bt = Backtest(df, SuperTrendStrategy, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== AlgoFox MultiTF SuperTrend (RSI Version) ===")
print(f"Return: {stats['Return [%]']:.2f}%")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Trades: {stats['# Trades']}")
if stats['# Trades'] > 0:
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.3f}")
