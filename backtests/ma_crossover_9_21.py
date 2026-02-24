"""
Strategy: MA Crossover 9/21
Source: TradingView Built-in
Logic: Buy when 9 EMA crosses above 21 EMA
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest, crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

data['ma9'] = data['Close'].ewm(span=9).mean()
data['ma21'] = data['Close'].ewm(span=21).mean()

class Strategy(Strategy):
    def init(self):
        self.ma9 = self.I(lambda: data['ma9'].values)
        self.ma21 = self.I(lambda: data['ma21'].values)
    
    def next(self):
        if len(self.data) < 25:
            return
        if crossover(self.ma9, self.ma21) and not self.position:
            self.buy(size=0.1)
        elif crossover(self.ma21, self.ma9) and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"ma_crossover_9_21,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
