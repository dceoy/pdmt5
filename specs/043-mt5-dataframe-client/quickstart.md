# Quickstart: Mt5 DataFrame Client

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
from pdmt5 import Mt5Config, Mt5DataClient

config = Mt5Config(
    login=12345678,
    password="your_password",
    server="Broker-Server",
    timeout=60000,
)

with Mt5DataClient(config=config) as client:
    account_df = client.account_info_as_df()
    rates_df = client.copy_rates_from_as_df(
        symbol="EURUSD",
        timeframe=mt5.TIMEFRAME_H1,
        date_from=datetime(2024, 1, 1),
        count=100,
        index_keys="time",
    )
```

## Notes

- Set `skip_to_datetime=True` on `_as_df` and `_as_dict` methods to keep raw times.
- Provide `index_keys` to set DataFrame indices when results are non-empty.
- Validation errors are raised before MT5 calls for invalid input ranges.
