"""
Strategy: Stochastic
Source: TradingView Built-in
Logic: Buy when %K crosses above %D in oversold, sell in overbought
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest, crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def stochastic(high, low, close, k_period=14, d_period=3):
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d = k.rolling(window=d_period).mean()
    return k, d

data['k'], data['d'] = stochastic(data['High'], data['Low'], data['Close'])

class Strategy(Strategy):
    def init(self):
        self.k = self.I(lambda: data['k'].values)
        self.d = self.I(lambda: data['d'].values)
    
    def next(self):
        if len(self.data) < 20:
            return
        k = self.k[-1]
        d = self.d[-1]
        k_prev = self.k[-2]
        d_prev = self.d[-2]
        
        # Buy when %K crosses above %D in oversold zone
        if k_prev <= d_prev and k > d and k < 20 and not self.position:
            self.buy(size=0.1)
        # Sell when %K crosses below %D in overbought zone
        elif k_prev >= d_prev and k < d and k > 80 and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"stochastic_oscillator,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
