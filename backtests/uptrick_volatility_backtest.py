"""
Strategy: Uptrick Volatility Aggregation Model
Source: TradingView - Popular
Pine: pine_scripts/uptrick_volatility_aggregation_model.pine

Logic: EMA crossover - Buy when fast EMA crosses above slow EMA
"""
import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover, FractionalBacktest

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

class VAMStrategy(Strategy):
    def init(self):
        self.ema_fast = self.I(lambda: pd.Series(self.data.Close).ewm(span=10).mean())
        self.ema_slow = self.I(lambda: pd.Series(self.data.Close).ewm(span=30).mean())
    
    def next(self):
        if len(self.data) < 31:
            return
        if crossover(self.ema_fast, self.ema_slow) and not self.position:
            self.buy()
        elif crossover(self.ema_slow, self.ema_fast) and self.position:
            self.sell()

bt = FractionalBacktest(data, VAMStrategy, cash=1000, commission=0)
stats = bt.run()

print(f"uptrick_volatility_aggregation_model,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
