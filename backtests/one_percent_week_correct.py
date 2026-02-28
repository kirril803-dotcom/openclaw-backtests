"""
One Percent A Week - CORRECT Backtest
Weekly strategy: Buy at 1% dip from Monday open, sell at 1% profit
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df['dayofweek'] = df['datetime'].dt.dayofweek
print(f"Data: {len(df)} hours")

# Find Monday open prices (first bar of each week)
df['is_monday'] = df['dayofweek'] == 0
df['is_first_bar_of_week'] = df['is_monday'] & (df['dayofweek'] != df['dayofweek'].shift(1))

# Get Monday open prices
monday_opens = df[df['is_first_bar_of_week']]['Open'].values
monday_indices = df[df['is_first_bar_of_week']].index.tolist()

print(f"Number of weeks (Mondays): {len(monday_opens)}")

# Strategy:
# 1. On Monday, set limit buy at 1% below Monday open
# 2. Set target at 1% above entry
# 3. Set stop at -0.5% (break-even protection)
# 4. Exit on Friday close OR when target/stop hit

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    entry_price = 0
    trades = 0
    wins = 0
    
    # Map monday opens to hours
    monday_data = {}
    for i, idx in enumerate(monday_indices):
        if i < len(monday_opens):
            monday_data[idx] = monday_opens[i]
    
    # Track position status
    pending_entry = None  # (entry_price, target, stop)
    
    for i in range(100, len(df)):
        price = df.iloc[i]['Close']
        low = df.iloc[i]['Low']
        high = df.iloc[i]['High']
        day = df.iloc[i]['dayofweek']
        is_monday = df.iloc[i]['is_first_bar_of_week']
        
        # New Monday - set pending order
        if is_monday and pos is None:
            monday_open = price
            entry_target = monday_open * 0.99  # 1% below
            pending_entry = (entry_target, monday_open * 1.01, monday_open * 0.995)  # (entry, target, stop)
        
        # Check for entry (price drops to 1% dip)
        if pending_entry is not None and pos is None:
            entry, target, stop = pending_entry
            # Check if price touched the entry level
            if low <= entry:
                btc = cash / entry
                cash = 0
                pos = 'long'
                entry_price = entry
                trades += 1
                pending_entry = None
        
        # Check for exit (target, stop, or Friday close)
        if pos == 'long':
            target = entry_price * 1.01
            stop = entry_price * 0.995
            
            # Exit conditions
            exit_triggered = False
            
            # Take profit
            if high >= target:
                cash = btc * target
                if target > entry_price:
                    wins += 1
                exit_triggered = True
            
            # Stop loss (break-even protection)
            elif low <= stop:
                cash = btc * stop
                exit_triggered = True
            
            # Friday close (day 4)
            elif day == 4:
                cash = btc * price
                if price > entry_price:
                    wins += 1
                exit_triggered = True
            
            if exit_triggered:
                pos = None
                btc = 0
                entry_price = 0
    
    # Close any remaining position
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    win_rate = wins / trades * 100 if trades > 0 else 0
    
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': win_rate}

r = backtest('One Percent A Week')
print(f"\n=== One Percent A Week (CORRECT) ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
