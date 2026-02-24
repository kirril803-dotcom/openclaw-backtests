"""
Strategy: Awesome Oscillator
Source: Custom
Logic: Buy when AO crosses zero, sell when crosses back
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest, crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def awesome_oscillator(high, low, fast=5, slow=34):
    median = (high + low) / 2
    ao = median.rolling(fast).mean() - median.rolling(slow).mean()
    return ao

data['ao'] = awesome_oscillator(data['High'], data['Low'])

class Strategy(Strategy):
    def init(self):
        self.ao = self.I(lambda: data['ao'].values)
    
    def next(self):
        if len(self.data) < 40:
            return
        if crossover(self.ao, [0]) and not self.position:
            self.buy(size=0.1)
        elif crossover([0], self.ao) and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"awesome_oscillator,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
