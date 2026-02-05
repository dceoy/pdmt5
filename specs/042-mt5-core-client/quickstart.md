# Quickstart: Mt5 Core Client

## Prerequisites

- Windows with MetaTrader 5 terminal installed
- Python 3.11+

## Install

```bash
pip install -U pdmt5 MetaTrader5
```

## Basic usage

```python
from datetime import datetime
import MetaTrader5 as mt5
from pdmt5 import Mt5Client

with Mt5Client() as client:
    version = client.version()
    account = client.account_info()
    terminal = client.terminal_info()
    symbols = client.symbols_get()
    ticks = client.copy_ticks_from(
        symbol="EURUSD",
        date_from=datetime(2024, 1, 1),
        count=10,
        flags=mt5.COPY_TICKS_ALL,
    )
```

## Notes

- Use the context manager to ensure `initialize` and `shutdown` are paired.
- Callers can provide login credentials via Mt5Client.initialize if needed.
- Methods return MT5 data or empty results; failures raise Mt5RuntimeError.
