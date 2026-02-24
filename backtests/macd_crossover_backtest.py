"""
Strategy: MACD Crossover
Source: TradingView Built-in
Logic: Buy when MACD line crosses above signal line
"""
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

class MACDStrategy(Strategy):
    def init(self):
        self.macd, self.signal = self.I(lambda: macd(self.data.Close))
    
    def next(self):
        if len(self.data) < 30:
            return
        if crossover(self.macd, self.signal) and not self.position:
            self.buy()
        elif crossover(self.signal, self.macd) and self.position:
            self.sell()

bt = Backtest(data, MACDStrategy, cash=1000, commission=0)
stats = bt.run()

print(f"macd_crossover,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
