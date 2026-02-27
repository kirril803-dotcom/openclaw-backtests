"""
Strategy: TASC 2026.03 One Percent A Week
Source: TradingView - TASC Issue March 2026

Logic:
1. Every Monday: Set weekly_open = Monday open price
2. Set limit_buy = weekly_open * 0.99 (1% dip)
3. If price drops to or below limit_buy, enter LONG
4. Set profit_target = entry_price * 1.01 (1% profit)
5. Set stop_loss = entry_price * 0.995 (0.5% loss = break-even)
6. Exit on: profit target hit, stop loss hit, or Friday close
"""
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
df['DayOfWeek'] = df.index.dayofweek  # 0=Monday, 4=Friday

class OnePercentAWeek(Strategy):
    def init(self):
        # Pre-calculate weekly opens and 1% dips
        self.weekly_open = None
        self.buy_target = None
        self.entry_price = None
        
    def next(self):
        day = self.data.DayOfWeek[-1]
        
        # NEW WEEK: On Monday, set up the weekly parameters
        if day == 0:  # Monday
            self.weekly_open = self.data.Open[-1]
            self.buy_target = self.weekly_open * 0.99
            
            # Reset position tracking for new week
            if self.position:
                # Still in position from last week - close it
                self.position.close()
        
        # If we don't have a position and have weekly setup
        if not self.position and self.weekly_open is not None:
            current_low = self.data.Low[-1]
            
            # Check if price hit the 1% dip (limit buy)
            if current_low <= self.buy_target:
                # Enter at the limit price (or current if already below)
                enter_price = min(self.buy_target, self.data.Close[-1])
                self.buy(size=0.1)  # 10% of equity
                self.entry_price = enter_price
        
        # If we have a position, manage it
        if self.position:
            current_price = self.data.Close[-1]
            high_price = self.data.High[-1]
            
            # Calculate targets
            profit_target = self.entry_price * 1.01  # 1% profit
            stop_loss = self.entry_price * 0.995      # 0.5% loss (break-even)
            
            # Exit on profit target
            if high_price >= profit_target:
                self.sell()
                
            # Exit on stop loss (break-even protection)
            elif current_price <= stop_loss:
                self.sell()
                
            # Exit on Friday close
            elif day == 4:  # Friday
                self.sell()

# Run backtest
bt = Backtest(df, OnePercentAWeek, cash=100_000_000, commission=0.001)
stats = bt.run()

print("=== TASC 2026.03 One Percent A Week ===")
print(f"Return: {stats['Return [%]']:.2f}%")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Trades: {stats['# Trades']}")
if stats['# Trades'] > 0:
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.3f}")
    print(f"Best Trade: {stats['Best Trade [%]']:.2f}%")
    print(f"Worst Trade: {stats['Worst Trade [%]']:.2f}%")

# Save to results.csv
import csv
with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'One Percent A Week',
        f"{stats['Return [%]']:.2f}",
        f"{stats['Max. Drawdown [%]']:.2f}",
        stats['# Trades'],
        f"{stats['Win Rate [%]']:.2f}" if stats['# Trades'] > 0 else '0',
        f"{stats['Sharpe Ratio']:.3f}" if stats['# Trades'] > 0 else '0'
    ])

print("\nResults saved!")
