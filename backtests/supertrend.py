"""
Strategy: Supertrend
Source: TradingView Built-in
Logic: Buy when close crosses above supertrend, sell when crosses below
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest, crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def supertrend(high, low, close, period=10, multiplier=3):
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    upper = ((high + low) / 2) + (multiplier * atr)
    lower = ((high + low) / 2) - (multiplier * atr)
    
    # Direction: 1 = bullish, -1 = bearish
    direction = pd.Series(0, index=close.index)
    for i in range(1, len(close)):
        if close.iloc[i] > upper.iloc[i]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lower.iloc[i]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i-1]
    
    return direction

data['supertrend'] = supertrend(data['High'], data['Low'], data['Close'])

class Strategy(Strategy):
    def init(self):
        self.st = self.I(lambda: data['supertrend'].values)
    
    def next(self):
        if len(self.data) < 15:
            return
        # Buy when trend changes to bullish (1)
        if self.st[-1] == 1 and self.st[-2] != 1 and not self.position:
            self.buy(size=0.1)
        # Sell when trend changes to bearish (-1)
        elif self.st[-1] == -1 and self.st[-2] != -1 and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"supertrend,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
