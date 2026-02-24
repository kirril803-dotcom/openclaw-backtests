# openclaw-backtests

TradingView indicator backtesting framework - converts Pine Script indicators to Python backtests.

## Structure

```
openclaw-backtests/
├── pine_scripts/     # Raw Pine Script source code
├── backtests/        # Python backtest files
├── data/             # BTC OHLCV CSV data
├── results.csv       # Master CSV with all backtest stats
└── requirements.txt  # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Run a backtest:
```bash
python backtests/<strategy_name>_backtest.py
```

## Results

See `results.csv` for backtest statistics across all strategies.
