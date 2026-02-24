"""
Strategy: RSI Reversal
Source: TradingView Built-in
Logic: Buy when RSI < 30, Sell when RSI > 70
"""
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

class RSIStrategy(Strategy):
    def init(self):
        self.rsi = self.I(lambda: rsi(self.data.Close))
    
    def next(self):
        if len(self.data) < 20:
            return
        rsi = self.rsi[-1]
        if rsi < 30 and not self.position:
            self.buy()
        elif rsi > 70 and self.position:
            self.sell()

bt = Backtest(data, RSIStrategy, cash=1000, commission=0)
stats = bt.run()

print(f"rsi_reversal,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
