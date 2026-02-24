"""
Strategy: EMA Pullback
Source: Custom
Logic: Buy when price pulls back to EMA and bounces
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

data['ema50'] = data['Close'].ewm(span=50).mean()

class Strategy(Strategy):
    def init(self):
        self.ema = self.I(lambda: data['ema50'].values)
    
    def next(self):
        if len(self.data) < 55:
            return
        
        close = self.data.Close[-1]
        open_price = self.data.Open[-1]
        ema = self.ema[-1]
        
        # Buy when price opens below EMA and closes above
        if open_price < ema and close > ema and not self.position:
            self.buy(size=0.1)
        # Sell when price opens above EMA and closes below
        elif open_price > ema and close < ema and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"ema_pullback,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
