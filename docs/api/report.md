# Report

::: pdmt5.report

## Overview

The report module extends the core `Mt5DataClient` functionality with reporting operations and data export capabilities. It provides formatted console output and export functionality to CSV and SQLite formats.

## Classes

### Mt5ReportClient
::: pdmt5.report.Mt5ReportClient
    options:
      show_bases: false

Enhanced data client that inherits from `Mt5DataClient` and adds presentation and export functionality for MetaTrader 5 data.

## Features

- **Pretty Printing**: Formatted console output for DataFrames and JSON data
- **SQLite Export**: Export data to SQLite database with deduplication
- **Print Methods**: Comprehensive printing for market data, trading info, and analysis
- **Inheritance**: All `Mt5DataClient` methods are available

## Usage Examples

### Basic Usage

```python
from pdmt5 import Mt5Config, Mt5ReportClient
import MetaTrader5 as mt5

config = Mt5Config(login=12345, password="pass", server="MetaQuotes-Demo")
client = Mt5ReportClient(mt5=mt5, config=config)

with client:
    # Print current positions
    client.print_positions()
    
    # Print MetaTrader 5 information
    client.print_mt5_info()
    
    # Print symbols
    client.print_symbols()
```

### Printing Market Data

```python
with client:
    # Print OHLCV rates
    client.print_rates("EURUSD", timeframe=mt5.TIMEFRAME_H1, count=10)
    
    # Print tick data
    client.print_ticks("EURUSD", count=20)
    
    # Print symbol information
    client.print_symbol_info("EURUSD")
    
    # Print market book
    client.print_market_book("EURUSD")
```

### Export to SQLite

```python
with client:
    # Print and export rates to SQLite
    client.print_rates(
        symbol="EURUSD",
        timeframe=mt5.TIMEFRAME_D1,
        count=365,
        sqlite3_file_path="data/trading.db",
        sqlite3_table="eurusd_rates"
    )
    
    # Print symbols with SQLite export
    client.print_symbols(
        sqlite3_file_path="data/market.db",
        sqlite3_table="symbols"
    )
```

### Trading and Position Data

```python
with client:
    # Print current orders
    client.print_orders()
    
    # Print margin requirements for a symbol
    client.print_margins("EURUSD")
    
    # Print historical orders
    client.print_history_orders(
        date_from=datetime(2024, 1, 1),
        date_to=datetime(2024, 12, 31)
    )
    
    # Print historical deals
    client.print_history_deals(
        date_from=datetime(2024, 1, 1),
        date_to=datetime(2024, 12, 31)
    )
```

### DataFrame and JSON Printing

```python
with client:
    # Get some data
    rates_df = client.copy_rates_from("EURUSD", mt5.TIMEFRAME_H1, datetime.now(), 100)
    account_info = client.account_info()
    
    # Print DataFrame with custom formatting
    Mt5ReportClient.print_df(rates_df, include_index=True)
    
    # Print data as formatted JSON
    Mt5ReportClient.print_json(account_info._asdict() if hasattr(account_info, '_asdict') else account_info)
```

### SQLite Export with Deduplication

```python
with client:
    # The print methods include optional SQLite export
    # Data is automatically deduplicated based on DataFrame index
    
    # Export ticks with deduplication
    client.print_ticks(
        symbol="EURUSD",
        count=1000,
        sqlite3_file_path="trading_data.db",
        sqlite3_table="eurusd_ticks"
    )
    
    # Export rates with deduplication  
    client.print_rates(
        symbol="EURUSD",
        timeframe=mt5.TIMEFRAME_H1,
        count=500,
        sqlite3_file_path="trading_data.db", 
        sqlite3_table="eurusd_h1_rates"
    )
```

## Print Methods Reference

### Market Data
- `print_rates(symbol, timeframe, count, sqlite3_file_path=None, sqlite3_table=None)` - Print OHLCV rates with optional SQLite export
- `print_ticks(symbol, count, sqlite3_file_path=None, sqlite3_table=None)` - Print tick data with optional SQLite export
- `print_symbol_info(symbol)` - Print symbol information
- `print_market_book(symbol)` - Print market depth/book data

### Symbols and Market
- `print_symbols(sqlite3_file_path=None, sqlite3_table=None)` - Print symbol list with optional SQLite export
- `print_mt5_info()` - Print MetaTrader 5 version and terminal information

### Trading and Positions
- `print_positions()` - Print open positions
- `print_orders()` - Print pending orders
- `print_margins(symbol)` - Print margin requirements for a symbol
- `print_history_orders(date_from, date_to)` - Print historical orders
- `print_history_deals(date_from, date_to)` - Print historical deals

### Static Utility Methods
- `print_df(df, include_index=True, display_max_columns=500, display_width=1500)` - Print DataFrame with custom formatting
- `print_json(data, indent=2)` - Print data as formatted JSON

## SQLite Export Features

All print methods that output DataFrames support optional SQLite export through `sqlite3_file_path` and `sqlite3_table` parameters. The SQLite export includes:

- **Automatic Deduplication**: Uses `drop_duplicates_in_sqlite3()` to prevent duplicate records
- **Table Creation**: Automatically creates tables if they don't exist
- **Index-based Deduplication**: Removes duplicates based on DataFrame index values

## Internal SQLite Methods

The following internal methods handle SQLite operations:

- `drop_duplicates_in_sqlite3(cursor, table)` - Remove duplicate records based on index
- `write_df_to_sqlite3(df, sqlite3_file_path, table)` - Write DataFrame to SQLite with deduplication

Example of incremental data collection:

```python
# This will only insert new ticks not already in the database
client.print_ticks(
    symbol="EURUSD",
    count=1000,
    sqlite3_file_path="trading.db",
    sqlite3_table="eurusd_ticks"
)

# Run again later - only new ticks will be added
client.print_ticks(
    symbol="EURUSD", 
    count=1000,
    sqlite3_file_path="trading.db",
    sqlite3_table="eurusd_ticks"
)
```

## Error Handling

All print methods handle errors gracefully:

```python
from pdmt5.mt5 import Mt5RuntimeError
from datetime import datetime

try:
    client.print_rates("INVALID_SYMBOL", timeframe=mt5.TIMEFRAME_H1, count=100)
except Mt5RuntimeError as e:
    print(f"Failed to print rates: {e}")
```

## Best Practices

1. **Use context manager** for automatic connection handling
2. **Create directories** before SQLite export to ensure path exists
3. **Use deduplication** for incremental SQLite updates
4. **Handle large datasets** carefully - use appropriate count limits
5. **Use static methods** for DataFrame and JSON formatting when data is already available
6. **Specify timeframes** using MetaTrader 5 constants (e.g., `mt5.TIMEFRAME_H1`)