# Quickstart: Mt5 Trading Client

## Prerequisites

- Windows with MetaTrader 5 terminal installed
- Python 3.11+

## Install

```bash
pip install -U pdmt5 MetaTrader5
```

## Basic usage

```python
from pdmt5 import Mt5Config, Mt5TradingClient

config = Mt5Config(
    login=12345678,
    password="your_password",
    server="Broker-Server",
    timeout=60000,
)

with Mt5TradingClient(config=config) as trader:
    result = trader.place_market_order(
        symbol="EURUSD",
        volume=0.1,
        order_side="BUY",
        dry_run=True,
    )
    metrics_df = trader.positions_with_metrics(symbol="EURUSD")
```

## Notes

- Use `dry_run=True` to validate orders without executing trades.
- Trading helpers raise Mt5TradingError on failed trade operations.
- Metrics helpers return DataFrames with derived fields when positions exist.
