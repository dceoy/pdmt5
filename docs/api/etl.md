# ETL

::: pdmt5.etl

## Overview

The etl module extends the core `Mt5DataClient` functionality with ETL (Extract, Transform, Load) operations and data export capabilities. It provides formatted console output and export functionality to CSV and SQLite formats.

## Classes

### Mt5EtlClient
::: pdmt5.etl.Mt5EtlClient
    options:
      show_bases: false

Enhanced data client that inherits from `Mt5DataClient` and adds presentation and export functionality for MetaTrader 5 data.

## Features

- **Pretty Printing**: Formatted console output for DataFrames and JSON data
- **CSV Export**: Export any DataFrame to CSV format
- **SQLite Export**: Export data to SQLite database with deduplication
- **Specialized Print Methods**: Tailored output for different data types
- **Inheritance**: All `Mt5DataClient` methods are available

## Usage Examples

### Basic Usage

```python
from pdmt5 import Mt5Config, Mt5EtlClient
import MetaTrader5 as mt5

config = Mt5Config(login=12345, password="pass", server="MetaQuotes-Demo")
printer = Mt5EtlClient(mt5=mt5, config=config)

with printer:
    # Pretty print current positions
    printer.print_positions()
    
    # Print account information as JSON
    printer.print_account_info()
```

### Printing Market Data

```python
with printer:
    # Print OHLCV rates
    printer.print_rates("EURUSD", timeframe="H1", count=10)
    
    # Print tick data
    printer.print_ticks("EURUSD", count=20)
    
    # Print symbol information
    printer.print_symbol_info("EURUSD")
```

### Export to CSV

```python
with printer:
    # Export rates to CSV
    printer.export_rates_to_csv(
        symbol="EURUSD",
        file_path="data/eurusd_rates.csv",
        timeframe="D1",
        count=365
    )
    
    # Export positions to CSV
    positions_df = printer.positions_get()
    printer.export_to_csv(positions_df, "data/positions.csv")
```

### Export to SQLite

```python
with printer:
    # Export deals to SQLite with deduplication
    printer.export_deals_to_sqlite(
        db_path="data/trading.db",
        table_name="deals",
        date_from=datetime(2024, 1, 1),
        date_to=datetime(2024, 12, 31)
    )
    
    # Export any DataFrame to SQLite
    symbols_df = printer.symbols_get()
    printer.export_to_sqlite(
        dataframe=symbols_df,
        db_path="data/market.db",
        table_name="symbols",
        if_exists="replace"
    )
```

### Specialized Print Methods

```python
with printer:
    # Print margin requirements
    printer.print_order_calc_margin(
        action="BUY",
        symbol="EURUSD",
        volume=1.0
    )
    
    # Print profit calculation
    printer.print_order_calc_profit(
        action="BUY",
        symbol="EURUSD",
        volume=1.0,
        price_open=1.1000,
        price_close=1.1050
    )
    
    # Print terminal information
    printer.print_terminal_info()
```

### Pretty Printing Options

```python
with printer:
    # Print with custom formatting
    rates_df = printer.copy_rates_from("EURUSD", mt5.TIMEFRAME_M5, datetime.now(), 100)
    
    # Basic pretty print
    printer.pretty_print_dataframe(rates_df)
    
    # Print as JSON
    printer.pretty_print_json({"symbol": "EURUSD", "timeframe": "M5", "count": 100})
```

## Print Methods Reference

### Market Data
- `print_rates()` - Print OHLCV rates
- `print_ticks()` - Print tick data
- `print_symbol_info()` - Print symbol information
- `print_symbol_info_tick()` - Print current tick

### Account & Trading
- `print_account_info()` - Print account details
- `print_positions()` - Print open positions
- `print_orders()` - Print pending orders
- `print_deals()` - Print historical deals
- `print_orders_history()` - Print order history

### Calculations
- `print_order_calc_margin()` - Print margin requirements
- `print_order_calc_profit()` - Print profit calculations
- `print_order_check()` - Print order validation results

### Terminal
- `print_terminal_info()` - Print MT5 terminal information
- `print_version()` - Print MT5 version

## Export Methods Reference

### CSV Export
- `export_to_csv()` - Export any DataFrame to CSV
- `export_rates_to_csv()` - Export OHLCV rates to CSV

### SQLite Export
- `export_to_sqlite()` - Export any DataFrame to SQLite
- `export_deals_to_sqlite()` - Export deals with deduplication

## Deduplication Feature

The SQLite export includes automatic deduplication based on the DataFrame index:

```python
# This will only insert new deals not already in the database
printer.export_deals_to_sqlite(
    db_path="trading.db",
    table_name="deals",
    date_from=datetime.now() - timedelta(days=7)
)
```

## Error Handling

All print and export methods handle errors gracefully:

```python
from pdmt5.mt5 import Mt5RuntimeError

try:
    printer.print_rates("INVALID_SYMBOL", timeframe="H1")
except Mt5RuntimeError as e:
    print(f"Failed to print rates: {e}")
```

## Best Practices

1. **Use context manager** for automatic connection handling
2. **Check file paths** before exporting to ensure directory exists
3. **Use deduplication** for incremental SQLite updates
4. **Handle large datasets** carefully - consider using date ranges
5. **Format timestamps** appropriately for your use case