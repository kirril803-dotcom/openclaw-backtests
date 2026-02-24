"""
Strategy: Bollinger Bands
Source: TradingView Built-in
Logic: Buy at lower band, sell at upper band
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def bb(close, window=20, num_std=2):
    ma = close.rolling(window=window).mean()
    std = close.rolling(window=window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return upper, ma, lower

data['upper'], data['mid'], data['lower'] = bb(data['Close'])

class Strategy(Strategy):
    def init(self):
        self.upper = self.I(lambda: data['upper'].values)
        self.lower = self.I(lambda: data['lower'].values)
    
    def next(self):
        if len(self.data) < 25:
            return
        price = self.data.Close[-1]
        lower = self.lower[-1]
        upper = self.upper[-1]
        
        if price < lower and not self.position:
            self.buy(size=0.1)
        elif price > upper and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"bollinger_bands,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
