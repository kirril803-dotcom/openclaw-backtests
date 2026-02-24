"""
Strategy: Parabolic SAR
Source: TradingView Built-in
Logic: Buy when SAR flips to below price, sell when flips above
"""
import pandas as pd
from backtesting import Strategy
from backtesting.lib import FractionalBacktest

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

def parabolic_sar(high, low, acceleration=0.02, maximum=0.2):
    sar = pd.Series(index=high.index, dtype=float)
    trend = pd.Series(1, index=high.index)  # 1 = up, -1 = down
    af = acceleration
    ep = high.iloc[0]  # extreme price
    sar.iloc[0] = low.iloc[0]
    
    for i in range(1, len(high)):
        if trend.iloc[i-1] == 1:
            sar.iloc[i] = sar.iloc[i-1] + af * (ep - sar.iloc[i-1])
            if low.iloc[i] < sar.iloc[i]:
                trend.iloc[i] = -1
                sar.iloc[i] = ep
                ep = low.iloc[i]
                af = acceleration
            else:
                trend.iloc[i] = 1
                if high.iloc[i] > ep:
                    ep = high.iloc[i]
                    af = min(af + acceleration, maximum)
        else:
            sar.iloc[i] = sar.iloc[i-1] + af * (ep - sar.iloc[i-1])
            if high.iloc[i] > sar.iloc[i]:
                trend.iloc[i] = 1
                sar.iloc[i] = ep
                ep = high.iloc[i]
                af = acceleration
            else:
                trend.iloc[i] = -1
                if low.iloc[i] < ep:
                    ep = low.iloc[i]
                    af = min(af + acceleration, maximum)
    
    return sar, trend

data['sar'], data['trend'] = parabolic_sar(data['High'], data['Low'])

class Strategy(Strategy):
    def init(self):
        self.sar = self.I(lambda: data['sar'].values)
        self.trend = self.I(lambda: data['trend'].values)
    
    def next(self):
        if len(self.data) < 5:
            return
        # Buy when trend flips to bullish (1)
        if self.trend[-1] == 1 and self.trend[-2] != 1 and not self.position:
            self.buy(size=0.1)
        # Sell when trend flips to bearish (-1)
        elif self.trend[-1] == -1 and self.trend[-2] != -1 and self.position:
            self.sell()

bt = FractionalBacktest(data, Strategy, cash=1000, commission=0)
stats = bt.run()

print(f"parabolic_sar,{stats['Return [%]']:.2f}%,{stats['Max. Drawdown [%]']:.2f}%,{stats['Sharpe Ratio']:.3f},N/A,{stats['Expectancy [%]']:.2f},{stats['# Trades']}")
