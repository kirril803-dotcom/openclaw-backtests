"""
Strategy: MACD Crossover
Source: TradingView Built-in
Logic: Buy when MACD crosses above signal
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest, crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def macd(close):
    ema_fast = close.ewm(span=12, adjust=False).mean()
    ema_slow = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal

data['macd'], data['signal'] = macd(data['Close'])

class Strategy(Strategy):
    def init(self):
        self.macd = self.I(lambda: data['macd'].values)
        self.signal = self.I(lambda: data['signal'].values)
    
    def next(self):
        if len(self.data) < 30:
            return
        if crossover(self.macd, self.signal) and not self.position:
            self.buy(size=0.1)
        elif crossover(self.signal, self.macd) and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"macd_crossover,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
