# pdmt5

Low-level MetaTrader 5 wrapper and pandas/dict conversion package

[![CI/CD](https://github.com/dceoy/pdmt5/actions/workflows/ci.yml/badge.svg)](https://github.com/dceoy/pdmt5/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)

## Overview

**pdmt5** is a Python package that provides a low-level wrapper around the MetaTrader 5 (MT5) API with pandas DataFrame and dictionary conversion helpers. It exposes raw MT5 API calls, converts results into pandas DataFrames and dicts, and provides canonical constant parsing for timeframes, tick copy flags, and order types.

High-level trading orchestration (market-order construction, margin-budget sizing, position lifecycle management, strategy or batch workflows) is out of scope. Those concerns belong in downstream applications or tools such as mt5cli.

See the [architecture contract](docs/architecture.md) for the stable root API,
return shapes, lifecycle and error semantics, dependency direction, and the
full list of responsibilities deliberately left to `mt5cli` or downstream
applications.

### Key Features

- **Pandas Integration**: DataFrame and dictionary helpers for easy analysis
- **Type Safety**: Full type hints with strict pyright checking and pydantic validation
- **Comprehensive MT5 Coverage**: Account info, market data, tick data, orders, positions, and more
- **Canonical MT5 Constants**: Shared parsing for timeframes, COPY_TICKS flags,
  and ORDER_TYPE values with official names, short aliases, or valid integers
- **Context Manager Support**: Clean initialization and cleanup with `with` statements; `Mt5DataClient` applies `Mt5Config` automatically
- **Time Series Ready**: OHLCV data with proper datetime indexing
- **Robust Error Handling**: Custom exceptions with detailed MT5 failure messages
- **Direct Order Primitives**: `order_check` / `order_send` wrappers with DataFrame/dict conversions

## Requirements

- **Operating System**: Windows (required by MetaTrader5 API)
- **Python**: 3.11 or higher
- **MetaTrader 5**: Terminal must be installed

## Installation

### Using pip

```bash
pip install -U pdmt5 MetaTrader5
```

### Using uv

```bash
git clone https://github.com/dceoy/pdmt5.git
cd pdmt5
uv sync
```

## Quick Start

```python
from datetime import datetime
from pdmt5 import Mt5DataClient, Mt5Config, parse_timeframe

# Configure connection
config = Mt5Config(
    login=12345678, password="your_password", server="YourBroker-Server", timeout=60000
)

# Use as context manager
with Mt5DataClient(config=config) as client:
    # Get account information as DataFrame
    account_info = client.account_info_as_df()
    print(account_info)

    # Get OHLCV data as DataFrame
    rates = client.copy_rates_from_as_df(
        symbol="EURUSD",
        timeframe=parse_timeframe("H1"),
        date_from=datetime(2024, 1, 1),
        count=100,
    )
    print(rates.head())

    # Get current positions as DataFrame
    positions = client.positions_get_as_df()
    print(positions)
```

## Core Components

### Mt5Client

The base client wrapper for all MetaTrader5 operations with context manager support:

- **Connection Management**:
  - `initialize()` - Establish connection with MT5 terminal (with optional path, login, password, server, timeout)
  - `login()` - Connect to trading account with credentials
  - `shutdown()` - Close MT5 terminal connection
  - Context manager support (`with` statement) for automatic initialization/cleanup (initialize only)
- **Terminal Information**:
  - `version()` - Get MT5 terminal version, build, and release date
  - `last_error()` - Get last error code and description
  - `account_info()` - Get current trading account information
  - `terminal_info()` - Get terminal status and settings
- **Symbol Operations**:
  - `symbols_total()` - Get total number of financial instruments
  - `symbols_get()` - Get all symbols or filter by group
  - `symbol_info()` - Get detailed data on specific symbol
  - `symbol_info_tick()` - Get last tick for symbol
  - `symbol_select()` - Show/hide symbol in MarketWatch
- **Market Depth**:
  - `market_book_add()` - Subscribe to Market Depth events
  - `market_book_get()` - Get current Market Depth data
  - `market_book_release()` - Unsubscribe from Market Depth
- **Market Data**:
  - `copy_rates_from()` - Get bars from specified date
  - `copy_rates_from_pos()` - Get bars from specified position
  - `copy_rates_range()` - Get bars for date range
  - `copy_ticks_from()` - Get ticks from specified date
  - `copy_ticks_range()` - Get ticks for date range
- **Order Operations**:
  - `orders_total()` - Get number of active orders
  - `orders_get()` - Get active orders with optional filters
  - `order_calc_margin()` - Calculate required margin
  - `order_calc_profit()` - Calculate potential profit
  - `order_check()` - Check if order can be placed
  - `order_send()` - Send order to trade server
- **Position Operations**:
  - `positions_total()` - Get number of open positions
  - `positions_get()` - Get open positions with optional filters
- **Trading History**:
  - `history_orders_total()` - Get number of historical orders
  - `history_orders_get()` - Get historical orders with filters
  - `history_deals_total()` - Get number of historical deals
  - `history_deals_get()` - Get historical deals with filters

### Mt5DataClient

Extends Mt5Client with pandas DataFrame and dictionary conversions:

- **Enhanced Connection**:
  - `initialize_and_login_mt5()` - Combined initialization and login with retry logic
  - Configurable retry attempts via `retry_count` parameter
- **DataFrame/Dictionary Conversions**: All methods have both `_as_df` and `_as_dict` variants:
  - `version_as_dict/df()` - MT5 version information
  - `last_error_as_dict/df()` - Last error details
  - `account_info_as_dict/df()` - Account information
  - `terminal_info_as_dict/df()` - Terminal information
  - `symbols_get_as_dicts/df()` - Symbol list with optional group filter
  - `symbol_info_as_dict/df()` - Single symbol information
  - `symbol_info_tick_as_dict/df()` - Last tick data
  - `market_book_get_as_dicts/df()` - Market depth data
- **OHLCV Data Methods**:
  - `copy_rates_from_as_dicts/df()` - Historical bars from date
  - `copy_rates_from_pos_as_dicts/df()` - Historical bars from position
  - `copy_rates_range_as_dicts/df()` - Historical bars for date range
- **Tick Data Methods**:
  - `copy_ticks_from_as_dicts/df()` - Historical ticks from date
  - `copy_ticks_range_as_dicts/df()` - Historical ticks for date range
- **Trading Data Methods**:
  - `orders_get_as_dicts/df()` - Active orders with filters
  - `order_check_as_dict/df()` - Order validation results
  - `order_send_as_dict/df()` - Order execution results
  - `positions_get_as_dicts/df()` - Open positions with filters
  - `history_orders_get_as_dicts/df()` - Historical orders with date/ticket/position filters
  - `history_deals_get_as_dicts/df()` - Historical deals with date/ticket/position filters
- **Features**:
  - Automatic time conversion to datetime objects
  - Optional DataFrame indexing with `index_keys` parameter
  - Input validation for dates, counts, and positions
  - Pydantic-based configuration via `Mt5Config`

### MT5 Constant Parsing

pdmt5 is the canonical source for parsing MT5 constants shared by CLI, HTTP API,
and other application layers. The constants module does not import
`MetaTrader5`, so it can be used for request validation and JSON schema
generation without a live terminal.

```python
from pdmt5 import parse_copy_ticks, parse_order_type, parse_timeframe
from pdmt5.constants import (
    list_copy_ticks_names,
    list_copy_ticks_values,
    list_order_type_names,
    list_order_type_values,
    list_timeframe_names,
    list_timeframe_values,
)

parse_timeframe("TIMEFRAME_M1")  # 1
parse_timeframe("M1")  # 1
parse_copy_ticks("COPY_TICKS_ALL")  # -1
parse_copy_ticks("ALL")  # -1
parse_order_type("ORDER_TYPE_BUY")  # 0
parse_order_type("BUY")  # 0

# Integer values are accepted only when they belong to the requested family.
parse_timeframe(16385)  # TIMEFRAME_H1
parse_order_type(16385)  # raises ValueError

# Use these helpers to build Pydantic JSON schema enums.
timeframe_schema = {
    "anyOf": [
        {"type": "string", "enum": list_timeframe_names()},
        {"type": "integer", "enum": list_timeframe_values()},
    ],
}
copy_ticks_schema = {
    "anyOf": [
        {"type": "string", "enum": list_copy_ticks_names()},
        {"type": "integer", "enum": list_copy_ticks_values()},
    ],
}
order_type_schema = {
    "anyOf": [
        {"type": "string", "enum": list_order_type_names()},
        {"type": "integer", "enum": list_order_type_values()},
    ],
}
```

### Configuration

```python
from pdmt5 import Mt5Config

config = Mt5Config(
    login=12345678,  # MT5 account number
    password="password",  # MT5 password
    server="Broker-Server",  # MT5 server name
    timeout=60000,  # Connection timeout in ms
)
```

## Examples

### Getting Historical Data

```python
from datetime import datetime
from pdmt5 import Mt5DataClient, parse_timeframe

with Mt5DataClient(config=config) as client:
    # Get last 1000 H1 bars for EURUSD as DataFrame
    df = client.copy_rates_from_as_df(
        symbol="EURUSD",
        timeframe=parse_timeframe("TIMEFRAME_H1"),
        date_from=datetime.now(),
        count=1000,
    )

    # Data includes: time, open, high, low, close, tick_volume, spread, real_volume
    print(df.columns)
    print(df.describe())
```

### Working with Tick Data

```python
from datetime import datetime, timedelta
from pdmt5 import parse_copy_ticks

with Mt5DataClient(config=config) as client:
    # Get ticks for the last hour as DataFrame
    ticks = client.copy_ticks_from_as_df(
        symbol="EURUSD",
        date_from=datetime.now() - timedelta(hours=1),
        count=10000,
        flags=parse_copy_ticks("COPY_TICKS_ALL"),
    )

    # Tick data includes: time, bid, ask, last, volume, flags
    print(ticks.head())
```

### Analyzing Positions

```python
with Mt5DataClient(config=config) as client:
    # Get all open positions as DataFrame
    positions = client.positions_get_as_df()

    if not positions.empty:
        # Calculate summary statistics
        summary = positions.groupby("symbol").agg({
            "volume": "sum",
            "profit": "sum",
            "price_open": "mean",
        })
        print(summary)
```

### Order Check and Send

```python
with Mt5DataClient(config=config) as client:
    # Validate an order request without sending
    request = {
        "action": 1,  # TRADE_ACTION_DEAL
        "symbol": "EURUSD",
        "volume": 0.1,
        "type": 0,  # ORDER_TYPE_BUY
        "type_filling": 1,
        "type_time": 0,
    }
    check = client.order_check_as_dict(request=request)
    print(f"Check retcode: {check['retcode']}")

    # Send the order to the trade server
    result = client.order_send_as_dict(request=request)
    print(f"Send retcode: {result['retcode']}")
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
uv run pytest tests/ -v

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
- **Testing**: pytest with 100% branch coverage enforcement
- **Documentation**: Google-style docstrings

## Error Handling

The package provides detailed error information:

```python
from pdmt5 import Mt5RuntimeError, parse_timeframe

try:
    with Mt5DataClient(config=config) as client:
        data = client.copy_rates_from(
            "INVALID", parse_timeframe("H1"), datetime.now(), 100
        )
except Mt5RuntimeError as e:
    print(f"MT5 Error: {e}")
    print("Inspect the exception message for the MT5 status details.")
```

## Timestamps and Timezones

MT5 epoch timestamps (`time`, `time_msc`, `time_setup`, etc.) are labels on the
**trade server's wall clock** (typically UTC+2 or UTC+3), not true UTC. pdmt5
converts them to **timezone-naive** `datetime64`/`Timestamp` values that
preserve those labels:

- Converted datetimes are naive and represent server time. Do **not** treat
  them as UTC; comparing them against `datetime.now(UTC)` or persisting them
  with a UTC label introduces a 2–3 hour bias.
- `date_from`/`date_to` arguments (e.g. in `history_deals_get`,
  `copy_rates_range`, `copy_ticks_range`) are compared against server-labeled
  epochs by the MetaTrader5 API, so pass datetimes expressed in server time.
- The official MQL5 docs call these epochs "UTC" because no timezone shift is
  applied to them, and they recommend `tzinfo=timezone.utc` so that the
  MetaTrader5 package does not shift naive datetimes by your local timezone.
  Both hold here: construct datetimes with `tzinfo=timezone.utc`, but choose
  wall-clock values that follow the trade server's clock.
- To skip the conversion and work with the raw epochs, pass
  `skip_to_datetime=True` to the `*_as_dict`/`*_as_df` methods.

## Limitations

- **Windows Only**: Due to MetaTrader5 API requirements
- **MT5 Terminal Required**: The MetaTrader 5 terminal must be installed
- **Single Thread**: MT5 API is not thread-safe
- **Server-Time Timestamps**: Returned datetimes are timezone-naive server
  time, not UTC (see [Timestamps and Timezones](#timestamps-and-timezones))

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
