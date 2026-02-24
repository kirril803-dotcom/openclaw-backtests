"""
Strategy: Uptrick Volatility Aggregation Model (VAM) - Simplified
Source: TradingView - Popular
Pine Script: pine_scripts/uptrick_volatility_aggregation_model.pine
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Ensure correct column names
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# VAM Strategy - simplified using price momentum
class VAMStrategy(Strategy):
    def init(self):
        # Use EMA crossover as signal
        self.ema_fast = self.I(lambda: pd.Series(self.data.Close).ewm(span=10).mean())
        self.ema_slow = self.I(lambda: pd.Series(self.data.Close).ewm(span=30).mean())
    
    def next(self):
        if len(self.data) < 31:
            return
        
        # Buy: fast EMA crosses above slow EMA
        if crossover(self.ema_fast, self.ema_slow) and not self.position:
            self.buy(size=0.1)  # Buy 10% of portfolio
        
        # Sell: fast EMA crosses below slow EMA
        elif crossover(self.ema_slow, self.ema_fast) and self.position:
            self.sell()

# Run backtest with high cash and fractional position
bt = Backtest(data, VAMStrategy, cash=100_000_000, commission=0.001)  # 100M cash
stats = bt.run()

# Print key metrics
print("=== Uptrick Volatility Aggregation Model (EMA Crossover) ===")
print(f"Return: {stats['Return [%]']:.2f}%")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Trades: {stats['# Trades']}")
if stats['# Trades'] > 0:
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.3f}")
