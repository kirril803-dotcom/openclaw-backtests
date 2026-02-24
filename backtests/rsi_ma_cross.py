"""
Strategy: RSI MA Cross
Source: Custom
Logic: Buy when RSI crosses above MA, sell when crosses below
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest, crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data['rsi'] = rsi(data['Close'])
data['rsi_ma'] = data['rsi'].rolling(9).mean()

class Strategy(Strategy):
    def init(self):
        self.rsi = self.I(lambda: data['rsi'].values)
        self.rsi_ma = self.I(lambda: data['rsi_ma'].values)
    
    def next(self):
        if len(self.data) < 25:
            return
        if crossover(self.rsi, self.rsi_ma) and not self.position:
            self.buy(size=0.1)
        elif crossover(self.rsi_ma, self.rsi) and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"rsi_ma_cross,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
