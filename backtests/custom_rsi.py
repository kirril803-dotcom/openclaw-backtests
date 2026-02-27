"""
Custom Backtester for BTC - No margin issues
"""
import pandas as pd
import numpy as np

data_path = 'C:/Users/Кирилл/.openclaw/workspace/openclaw-backtests/data/btc_data_clean.csv'
df = pd.read_csv(data_path, parse_dates=['datetime'])
df.columns = ['datetime', 'Open', 'High', 'Low', 'Close', 'Volume']

# RSI
def rsi(close, period=7):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    return 100 - (100 / (1 + gain / loss))

df['RSI'] = rsi(df['Close'], 7)

# Backtest
cash = 10000
btc_holdings = 0
trades = []
position = None
entry_price = 0

for i in range(20, len(df)):
    rsi_val = df.iloc[i]['RSI']
    price = df.iloc[i]['Close']
    
    # Buy signal
    if rsi_val < 40 and position is None:
        btc_holdings = cash / price
        position = 'long'
        entry_price = price
        trades.append(('BUY', price, i))
        cash = 0
    
    # Sell signal
    elif position == 'long' and rsi_val > 60:
        cash = btc_holdings * price
        profit = (price - entry_price) / entry_price * 100
        trades.append(('SELL', price, i, profit))
        btc_holdings = 0
        position = None

# Close any open position
if position == 'long':
    final_price = df.iloc[-1]['Close']
    cash = btc_holdings * final_price
    trades.append(('CLOSE', final_price, len(df)-1, (final_price - entry_price) / entry_price * 100))

final_value = cash
roi = (final_value - 10000) / 10000 * 100

print("=== Custom RSI Backtest ===")
print(f"Initial: $10,000")
print(f"Final: ${final_value:.2f}")
print(f"ROI: {roi:.2f}%")
print(f"Trades: {len([t for t in trades if t[0] in ['BUY','SELL']])}")

buy_trades = [t for t in trades if t[0] == 'BUY']
sell_trades = [t for t in trades if t[0] == 'SELL']
print(f"Buy signals: {len(buy_trades)}")
print(f"Sell signals: {len(sell_trades)}")

# Calculate drawdown
values = []
running_cash = 10000
btc = 0
pos = None
entry = 0

for i in range(20, len(df)):
    rsi_v = df.iloc[i]['RSI']
    price = df.iloc[i]['Close']
    
    if rsi_v < 40 and pos is None:
        btc = running_cash / price
        pos = 'long'
        entry = price
        running_cash = 0
    elif pos == 'long' and rsi_v > 60:
        running_cash = btc * price
        pos = None
    
    if pos == 'long':
        val = btc * price
    else:
        val = running_cash
    values.append(val)

max_val = max(values)
drawdowns = [(max_val - v) / max_val * 100 for v in values]
max_dd = max(drawdowns)

print(f"Max Drawdown: {max_dd:.2f}%")

if len(sell_trades) > 0:
    wins = [t[3] for t in sell_trades if t[3] > 0]
    losses = [t[3] for t in sell_trades if t[3] <= 0]
    win_rate = len(wins) / len(sell_trades) * 100 if sell_trades else 0
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Avg Win: {np.mean(wins):.2f}%" if wins else "")
    print(f"Avg Loss: {np.mean(losses):.2f}%" if losses else "")
