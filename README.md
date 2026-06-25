# pdmt5

Pandas-based data handler for MetaTrader 5

[![CI/CD](https://github.com/dceoy/pdmt5/actions/workflows/ci.yml/badge.svg)](https://github.com/dceoy/pdmt5/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)

## Overview

**pdmt5** is a Python package that provides a pandas-based interface for MetaTrader 5 (MT5), making it easier to work with financial market data in Python. It provides helpers to convert MT5's native data structures into pandas DataFrames and dictionaries, enabling seamless integration with data science workflows.

### Ecosystem and Responsibility Boundary

**pdmt5** sits at the core of a layered ecosystem:

| Layer           | Package                  | Responsibility                                                                                                                                                                                                                                                                            |
| --------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Core adapter    | **pdmt5** (this package) | MT5 connection lifecycle, low-level MT5 method wrappers, DataFrame/dict conversion helpers, canonical MT5 constant parsing, minimal direct order primitives around `order_check` / `order_send`                                                                                           |
| Operational SDK | **mt5cli**               | Canonical downstream operational SDK / CLI / batch processing / SQLite history layer built on top of `pdmt5`. Generic operational orchestration belongs here: margin-budget sizing, normalised execution-result handling, broker constraint pre-checks, and downstream trading workflows. |
| HTTP adapter    | **mt5api**               | Sibling HTTP/FastAPI adapter that exposes `pdmt5` over a REST interface.                                                                                                                                                                                                                  |
| Strategy apps   | _(downstream)_           | Signal generation, risk policy, backtesting, optimisation, and strategy-specific order decisions. These concerns belong in the application layer, not in `pdmt5` or `mt5cli`.                                                                                                             |

`pdmt5` does **not** depend on `mt5cli`.

### Key Features

- 📊 **Pandas Integration**: DataFrame and dictionary helpers for easy analysis
- 🔧 **Type Safety**: Full type hints with strict pyright checking and pydantic validation
- 🏦 **Comprehensive MT5 Coverage**: Account info, market data, tick data, orders, positions, and more
- 🧭 **Canonical MT5 Constants**: Shared parsing for timeframes, COPY_TICKS flags,
  and ORDER_TYPE values with official names, short aliases, or valid integers
- 🚀 **Context Manager Support**: Clean initialization and cleanup with `with` statements (initialize only)
- 📈 **Time Series Ready**: OHLCV data with proper datetime indexing
- 🛡️ **Robust Error Handling**: Custom exceptions with detailed MT5 error information
- 💰 **Direct Order Primitives**: `order_check` / `order_send` wrappers with retcode validation
- 🧪 **Dry Run Mode**: Test order requests without executing real trades

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
    login=12345678,
    password="your_password",
    server="YourBroker-Server",
    timeout=60000
)

# Use as context manager
with Mt5DataClient(config=config) as client:
    # Optional: login when credentials are provided
    client.login(config.login, config.password, config.server)

    # Get account information as DataFrame
    account_info = client.account_info_as_df()
    print(account_info)

    # Get OHLCV data as DataFrame
    rates = client.copy_rates_from_as_df(
        symbol="EURUSD",
        timeframe=parse_timeframe("H1"),
        date_from=datetime(2024, 1, 1),
        count=100
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
from pdmt5 import (
    list_copy_ticks_names,
    list_copy_ticks_values,
    list_order_type_names,
    list_order_type_values,
    list_timeframe_names,
    list_timeframe_values,
    parse_copy_ticks,
    parse_order_type,
    parse_timeframe,
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

### Mt5TradingClient

Trading client that extends `Mt5DataClient` with direct order primitives and
convenience wrappers. Methods are classified as follows:

- **Core MT5 primitives** — thin wrappers or constant mappings directly over the
  MetaTrader5 API:
  - `mt5_successful_trade_retcodes` — set of `TRADE_RETCODE_*` values indicating success
  - `mt5_failed_trade_retcodes` — set of `TRADE_RETCODE_*` values indicating failure

- **Convenience wrappers** — slightly higher-level helpers closely coupled to a
  single MT5 call:
  - `place_market_order()` — builds a `TRADE_ACTION_DEAL` request and sends/checks it
  - `calculate_minimum_order_margin()` — combines `symbol_info` + `order_calc_margin`
    to return the margin for the minimum allowable volume
  - `fetch_latest_rates_as_df()` — calls `copy_rates_from_pos_as_df` from position 0
    after resolving a `granularity` string (e.g. `"M1"`, `"H1"`) via `parse_timeframe`
  - `fetch_latest_ticks_as_df()` — calls `copy_ticks_range_as_df` centred on the last tick

- **Error handling**: `Mt5TradingError` (extends `Mt5RuntimeError`) is raised when
  an order operation returns a failed retcode and `raise_on_error=True`.

### Configuration

```python
from pdmt5 import Mt5Config

config = Mt5Config(
    login=12345678,          # MT5 account number
    password="password",     # MT5 password
    server="Broker-Server",  # MT5 server name
    timeout=60000           # Connection timeout in ms
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
        count=1000
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
        flags=parse_copy_ticks("COPY_TICKS_ALL")
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
        summary = positions.groupby('symbol').agg({
            'volume': 'sum',
            'profit': 'sum',
            'price_open': 'mean'
        })
        print(summary)
```

### Trading Operations

```python
from pdmt5 import Mt5TradingClient

with Mt5TradingClient(config=config) as trader:
    # Place a market buy order
    order_result = trader.place_market_order(
        symbol="EURUSD",
        volume=0.1,
        order_side="BUY",
        order_filling_mode="IOC",  # Immediate or Cancel
        order_time_mode="GTC"      # Good Till Cancelled
    )
    print(f"Order placed: {order_result['retcode']}")

    # Dry run: validate without executing
    check_result = trader.place_market_order(
        symbol="EURUSD",
        volume=0.1,
        order_side="SELL",
        dry_run=True,
    )
    print(f"Check result: {check_result['retcode']}")

    # Calculate minimum margin for a position
    min_margin = trader.calculate_minimum_order_margin("EURUSD", "BUY")
    print(f"Min volume: {min_margin['volume']}, min margin: {min_margin['margin']}")

    # Fetch recent OHLC bars
    rates_df = trader.fetch_latest_rates_as_df(
        symbol="EURUSD",
        granularity="M15",
        count=100,
    )
    print(rates_df.tail())

    # Fetch recent tick data
    ticks_df = trader.fetch_latest_ticks_as_df(symbol="EURUSD", seconds=60)
    print(f"Received {len(ticks_df)} ticks")
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
- **Testing**: pytest with coverage tracking (minimum 90%)
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
