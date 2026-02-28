"""
Connors RSI
"""
import pandas as pd
import numpy as np
import csv

df = pd.read_csv('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_hourly.csv')
print(f"Data: {len(df)} hours")

# RSI (3)
delta = df['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=3).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=3).mean()
rs = gain / loss
df['RSI3'] = 100 - (100 / (1 + rs))

# Up/Down Length RSI
df['UpDown'] = np.where(df['Close'] > df['Close'].shift(1), 1, 
                         np.where(df['Close'] < df['Close'].shift(1), -1, 0))
df['Streak'] = df['UpDown'].groupby((df['UpDown'] != df['UpDown'].shift()).cumsum()).cumsum()
delta2 = df['Streak'].diff()
gain2 = delta2.where(delta2 > 0, 0).rolling(window=2).mean()
loss2 = (-delta2.where(delta2 < 0, 0)).rolling(window=2).mean()
rs2 = gain2 / loss2
df['StreakRSI'] = 100 - (100 / (1 + rs2))

# Percent Rank
df['ROC1'] = df['Close'].pct_change()
df['PercentRank'] = df['ROC1'].rolling(100).apply(lambda x: (x < x.iloc[-1]).sum() / len(x) * 100, raw=False)

# Connors RSI
df['CRSI'] = (df['RSI3'] + df['StreakRSI'].fillna(50) + df['PercentRank'].fillna(50)) / 3

# Buy when CRSI < 10, sell when > 90
df['Buy'] = (df['CRSI'] < 10) & (df['CRSI'].shift(1) >= 10)
df['Sell'] = (df['CRSI'] > 90) & (df['CRSI'].shift(1) <= 90)

def backtest(name, initial_cash=10000):
    cash = initial_cash
    btc = 0
    pos = None
    trades = 0
    
    for i in range(110, len(df)):
        price = df.iloc[i]['Close']
        
        if pos is None and df.iloc[i]['Buy']:
            btc = cash / price
            cash = 0
            pos = 'long'
            trades += 1
        elif pos == 'long' and df.iloc[i]['Sell']:
            cash = btc * price
            pos = None
            btc = 0
    
    if pos:
        cash = btc * df.iloc[-1]['Close']
    
    roi = (cash - initial_cash) / initial_cash * 100
    return {'name': name, 'roi': roi, 'trades': trades}

r = backtest('Connors RSI')
print(f"\n=== Connors RSI ===")
print(f"ROI: {r['roi']:.2f}% | Trades: {r['trades']}")

with open('C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/results.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([r['name'], f"{r['roi']:.2f}%", "N/A", "N/A", "N/A", "N/A", r['trades']])
print("Saved!")
