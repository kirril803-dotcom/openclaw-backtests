"""
Strategy: Uptrick Volatility Aggregation Model (VAM)
Source: TradingView - Popular
Pine Script: pine_scripts/uptrick_volatility_aggregation_model.pine

=== BACKTEST RESULTS ===
(To be filled after running)
=======================
"""
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Load data
data_path = 'data/btc_data.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Ensure correct column names
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# VAM Strategy - 5-speed volatility ensemble
class VAMStrategy(Strategy):
    score_buy = 0.10
    score_sell = -0.10
    
    # Speed parameters (simplified from Pine)
    len1, len2, len3, len4, len5 = 8, 10, 14, 20, 28
    mult1, mult2, mult3, mult4, mult5 = 1.05, 1.10, 1.15, 1.20, 1.25
    band1, band2, band3, band4, band5 = 1.15, 1.20, 1.25, 1.30, 1.35
    smooth1, smooth2, smooth3, smooth4, smooth5 = 2, 2, 3, 3, 4
    
    def init(self):
        # Calculate True Range
        self.tr = self.I(talib.TRANGE, self.data.High, self.data.Low, self.data.Close)
        
        # Calculate 5 speed layers (simplified EMA-based)
        self.r1_1 = self.I(lambda: talib.EMA(self.tr, self.len1) * self.mult1)
        self.r1_2 = self.I(lambda: talib.EMA(self.tr, self.len2) * self.mult2)
        self.r1_3 = self.I(lambda: talib.EMA(self.tr, self.len3) * self.mult3)
        self.r1_4 = self.I(lambda: talib.EMA(self.tr, self.len4) * self.mult4)
        self.r1_5 = self.I(lambda: talib.EMA(self.tr, self.len5) * self.mult5)
        
        # Simplified: use price position vs ATR as proxy for score
        # Higher = more bullish, Lower = more bearish
        atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        self.score = self.I(lambda: (self.data.Close - self.data.Open) / atr)
    
    def next(self):
        if len(self.data) < 30:
            return
        
        score = self.score[-1]
        prev_score = self.score[-2] if len(self.data) > 1 else score
        
        # Buy: score crosses above buy threshold
        if prev_score <= self.score_buy and score > self.score_buy and not self.position:
            self.buy()
        
        # Sell: score crosses below sell threshold
        elif prev_score >= self.score_sell and score < self.score_sell and self.position:
            self.sell()

# Run backtest
bt = Backtest(data, VAMStrategy, cash=1000, commission=0)
stats = bt.run()
print(stats)
