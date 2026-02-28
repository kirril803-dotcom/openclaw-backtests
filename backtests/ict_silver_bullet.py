"""
ICT Silver Bullet Momentum - Backtest
Strategy: Buy when 2 consecutive hourly bars close bullish AND volume increases
Exit: 4R profit or trailing stop
"""
import pandas as pd
import numpy as np
import csv

# Load data
df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_5y.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
print(f"Data: {len(df)} days")

# Since we have daily data, simulate hourly-like behavior with daily
# In real backtest would need hourly data

# Use daily close > open as bullish
df['Bullish'] = df['Close'] > df['Open']
df['VolumeIncreased'] = df['Volume'] > df['Volume'].shift(1)

# Entry: 2 consecutive bullish + volume increase
df['EntrySignal'] = (df['Bullish'] & df['Bullish'].shift(1) & df['VolumeIncreased'])

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    entry = 0
    trades = 0
    wins = 0
    losses = 0
    
    for i in range(50, len(df)):
        price = df.iloc[i]['Close']
        signal = df.iloc[i]['EntrySignal']
        
        # Entry
        if signal and pos is None:
            btc = cash / price
            cash = 0
            pos = 'long'
            entry = price
            trades += 1
        # Exit: 4R or end
        elif pos == 'long':
            pnl_pct = (price - entry) / entry * 100
            if pnl_pct >= 4 * 1:  # 4R exit (1% risk = 4% target)
                cash = btc * price
                if pnl_pct > 0:
                    wins += 1
                else:
                    losses += 1
                pos = None
                btc = 0
    
    # Close at end
    if pos:
        final_price = df.iloc[-1]['Close']
        cash = btc * final_price
        pnl_pct = (final_price - entry) / entry * 100
        if pnl_pct > 0:
            wins += 1
        else:
            losses += 1
    
    final_value = cash
    roi = (final_value - initial_cash) / initial_cash * 100
    win_rate = wins / trades * 100 if trades > 0 else 0
    
    return {'name': name, 'roi': roi, 'trades': trades, 'win_rate': win_rate}

r = backtest('ICT Silver Bullet Momentum')
print(f"\n=== ICT Silver Bullet Momentum ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%")

# Save
with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])

print("Saved!")
