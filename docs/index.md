# pdmt5 API Documentation

Low-level MetaTrader 5 wrapper and pandas/dict conversion package.

## Overview

pdmt5 is a Python library that provides a low-level wrapper around the MetaTrader 5 (MT5) API with pandas DataFrame and dictionary conversion helpers. It simplifies data access and conversion for financial market data analysis.

## Features

- **MetaTrader 5 Integration**: Direct connection to MetaTrader 5 platform (Windows only)
- **Pandas-based**: Leverages pandas for efficient data manipulation
- **Canonical MT5 Constants**: Shared parsers for timeframes, COPY_TICKS flags,
  and ORDER_TYPE values using official names, short aliases, or valid integers
- **Type Safety**: Built with pydantic for robust data validation

## Installation

```bash
pip install pdmt5
```

### Quick Start

```python
from pdmt5 import (
    Mt5Client,
    Mt5Config,
    Mt5DataClient,
    parse_copy_ticks,
    parse_timeframe,
)
import MetaTrader5 as mt5
from datetime import datetime

# Configure connection
config = Mt5Config(
    login=12345678,
    password="your_password",
    server="YourBroker-Server",
    timeout=60000,
)

# Low-level API access with context manager
with Mt5Client() as client:
    client.initialize()
    client.login(config.login, config.password, config.server)
    account = client.account_info()
    rates = client.copy_rates_from("EURUSD", mt5.TIMEFRAME_H1, datetime.now(), 100)

# Pandas-friendly interface with context-managed initialization
with Mt5DataClient(config=config) as client:
    # Optional: login when credentials are provided
    client.login(config.login, config.password, config.server)

    # Get symbol information as DataFrame
    symbols_df = client.symbols_get_as_df()
    # Get OHLCV data as DataFrame
    rates_df = client.copy_rates_from_as_df(
        "EURUSD", parse_timeframe("H1"), datetime.now(), 100
    )
    # Get account info as DataFrame
    account_df = client.account_info_as_df()

# Parse MT5 constants without importing the MetaTrader5 module
timeframe = parse_timeframe("TIMEFRAME_H1")  # 16385
tick_flags = parse_copy_ticks("ALL")  # -1
```

## Requirements

- Python 3.11+
- Windows OS (MetaTrader 5 requirement)
- MetaTrader 5 platform

## API Reference

Browse the API documentation to learn about available modules and functions:

- [Mt5Client](api/mt5.md) - Base client for low-level MT5 API access with context manager support
- [Constants](api/constants.md) - Canonical MT5 constant parsing and schema helper values
- [Mt5DataClient & Mt5Config](api/dataframe.md) - Pandas-friendly data client with DataFrame conversions
- [Utility Functions](api/utils.md) - Helper decorators and functions for data processing

## Development

This project follows strict code quality standards:

- Type hints required (strict mode)
- Comprehensive linting with Ruff
- Test coverage tracking
- Google-style docstrings

## License

MIT License - see [LICENSE](https://github.com/dceoy/pdmt5/blob/main/LICENSE) file for details.
