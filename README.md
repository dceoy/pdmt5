# pdmt5

Pandas-based data handler for MetaTrader 5

[![CI/CD](https://github.com/dceoy/pdmt5/actions/workflows/ci.yml/badge.svg)](https://github.com/dceoy/pdmt5/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)

## Overview

**pdmt5** is a Python package that provides a pandas-based interface for MetaTrader 5 (MT5), making it easier to work with financial market data in Python. It automatically converts MT5's native data structures into pandas DataFrames, enabling seamless integration with data science workflows.

### Key Features

- 📊 **Pandas Integration**: All data returned as pandas DataFrames for easy analysis
- 🔧 **Type Safety**: Full type hints with strict pyright checking and pydantic validation
- 🏦 **Comprehensive MT5 Coverage**: Account info, market data, tick data, orders, positions, and more
- 🚀 **Context Manager Support**: Clean initialization and cleanup with `with` statements
- 📈 **Time Series Ready**: OHLCV data with proper datetime indexing
- 🛡️ **Robust Error Handling**: Custom exceptions with detailed MT5 error information

## Requirements

- **Operating System**: Windows (required by MetaTrader5 API)
- **Python**: 3.11 or higher
- **MetaTrader 5**: Terminal must be installed

## Installation

### From GitHub

```bash
git clone https://github.com/dceoy/pdmt5.git
pip install -U --no-cache-dir ./pdmt5
```

### Using uv (recommended for development)

```bash
git clone https://github.com/dceoy/pdmt5.git
cd pdmt5
uv sync
```

## Quick Start

```python
import pdmt5
from pdmt5 import Mt5DataClient, Mt5Config

# Configure connection
config = Mt5Config(
    login=12345678,
    password="your_password",
    server="YourBroker-Server",
    timeout=60000,
    portable=False
)

# Use as context manager
with Mt5DataClient(config=config) as client:
    # Get account information
    account_info = client.get_account_info()
    print(account_info)

    # Get OHLCV data
    rates = client.copy_rates_from(
        symbol="EURUSD",
        timeframe=pdmt5.TIMEFRAME_H1,
        date_from=datetime(2024, 1, 1),
        count=100
    )
    print(rates.head())

    # Get current positions
    positions = client.get_positions()
    print(positions)
```

## Core Components

### Mt5DataClient

The main interface for interacting with MetaTrader 5:

- **Account Operations**: `get_account_info()`, `get_terminal_info()`
- **Market Data**: `copy_rates_*()` methods for OHLCV data
- **Tick Data**: `copy_ticks_*()` methods for tick-level data
- **Trading Info**: `get_orders()`, `get_positions()`, `get_deals()`
- **Symbol Info**: `get_symbols()`, `get_symbol_info()`

### Constants

Comprehensive enums for MT5 constants:

```python
from pdmt5 import (
    TIMEFRAME_M1, TIMEFRAME_H1, TIMEFRAME_D1,
    ORDER_TYPE_BUY, ORDER_TYPE_SELL,
    POSITION_TYPE_BUY, POSITION_TYPE_SELL,
    TICK_FLAG_BID, TICK_FLAG_ASK
)
```

### Configuration

```python
from pdmt5 import Mt5Config

config = Mt5Config(
    login=12345678,          # MT5 account number
    password="password",     # MT5 password
    server="Broker-Server",  # MT5 server name
    timeout=60000,          # Connection timeout in ms
    portable=False          # Use portable mode
)
```

## Examples

### Getting Historical Data

```python
import pdmt5
from datetime import datetime

with Mt5DataClient(config=config) as client:
    # Get last 1000 H1 bars for EURUSD
    df = client.copy_rates_from(
        symbol="EURUSD",
        timeframe=pdmt5.TIMEFRAME_H1,
        date_from=datetime.now(),
        count=1000
    )

    # Data includes: time, open, high, low, close, tick_volume, spread, real_volume
    print(df.columns)
    print(df.describe())
```

### Working with Tick Data

```python
with Mt5DataClient(config=config) as client:
    # Get ticks for the last hour
    ticks = client.copy_ticks_from(
        symbol="EURUSD",
        date_from=datetime.now() - timedelta(hours=1),
        count=10000,
        flags=pdmt5.COPY_TICKS_ALL
    )

    # Tick data includes: time, bid, ask, last, volume, flags
    print(ticks.head())
```

### Analyzing Positions

```python
with Mt5DataClient(config=config) as client:
    # Get all open positions
    positions = client.get_positions()

    if not positions.empty:
        # Calculate summary statistics
        summary = positions.groupby('symbol').agg({
            'volume': 'sum',
            'profit': 'sum',
            'price_open': 'mean'
        })
        print(summary)
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/dceoy/pdmt5.git
cd pdmt5

# Install with uv
uv sync

# Run tests
uv run pytest test/ -v

# Run type checking
uv run pyright .

# Run linting
uv run ruff check --fix .
uv run ruff format .
```

### Code Quality

This project maintains high code quality standards:

- **Type Checking**: Strict mode with pyright
- **Linting**: Comprehensive ruff configuration with 40+ rule categories
- **Testing**: pytest with coverage tracking (minimum 50%)
- **Documentation**: Google-style docstrings

## Error Handling

The package provides detailed error information:

```python
from pdmt5 import Mt5Error

try:
    with Mt5DataClient(config=config) as client:
        data = client.copy_rates_from("INVALID", pdmt5.TIMEFRAME_H1, datetime.now(), 100)
except Mt5Error as e:
    print(f"MT5 Error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Description: {e.description}")
```

## Limitations

- **Windows Only**: Due to MetaTrader5 API requirements
- **MT5 Terminal Required**: The MetaTrader 5 terminal must be installed
- **Single Thread**: MT5 API is not thread-safe

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Ensure tests pass and coverage is maintained
4. Submit a pull request

See [CLAUDE.md](CLAUDE.md) for development guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Daichi Narushima, Ph.D.

## Acknowledgments

- MetaTrader 5 for providing the Python API
- The pandas community for the excellent data manipulation tools
