"""
Strategy: ADX Trend
Source: TradingView Built-in
Logic: Buy when ADX > 25 and +DI crosses above -DI
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest, crossover

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def adx(high, low, close, period=14):
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    
    return adx, plus_di, minus_di

data['adx'], data['plus_di'], data['minus_di'] = adx(data['High'], data['Low'], data['Close'])

class Strategy(Strategy):
    def init(self):
        self.adx = self.I(lambda: data['adx'].values)
        self.plus_di = self.I(lambda: data['plus_di'].values)
        self.minus_di = self.I(lambda: data['minus_di'].values)
    
    def next(self):
        if len(self.data) < 30:
            return
        # Buy when ADX > 25 and +DI crosses above -DI
        if self.adx[-1] > 25 and crossover(self.plus_di, self.minus_di) and not self.position:
            self.buy(size=0.1)
        # Sell when -DI crosses above +DI
        elif crossover(self.minus_di, self.plus_di) and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"adx_trend,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
