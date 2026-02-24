"""
Strategy: Price Channel
Source: TradingView Built-in
Logic: Buy when price breaks above channel, sell when breaks below
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest, crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

data['upper_channel'] = data['High'].rolling(20).max()
data['lower_channel'] = data['Low'].rolling(20).min()

class Strategy(Strategy):
    def init(self):
        self.upper = self.I(lambda: data['upper_channel'].values)
        self.lower = self.I(lambda: data['lower_channel'].values)
    
    def next(self):
        if len(self.data) < 25:
            return
        price = self.data.Close[-1]
        upper = self.upper[-1]
        lower = self.lower[-1]
        
        if price > upper and not self.position:
            self.buy(size=0.1)
        elif price < lower and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"price_channel_breakout,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
