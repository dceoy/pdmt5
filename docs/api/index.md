# API Reference

This section contains the complete API documentation for pdmt5.

## Modules

The pdmt5 package consists of the following modules:

### [Mt5Client](mt5.md)
Base client class for MetaTrader 5 operations with connection management, low-level API access, and error handling (`Mt5RuntimeError`).

### [Mt5DataClient & Mt5Config](dataframe.md)
Core data client functionality and configuration, providing pandas-friendly interface to MetaTrader 5.

### [Mt5ReportClient](report.md)
Reporting operations and data export functionality for MetaTrader 5 data.

## Architecture Overview

The package follows a layered architecture:

1. **Base Layer** (`mt5.py`): Provides the base `Mt5Client` class with low-level MT5 API access and `Mt5RuntimeError` exception
2. **Core Layer** (`dataframe.py`): Extends `Mt5Client` with configuration (`Mt5Config`) and pandas-friendly `Mt5DataClient` class
3. **Presentation Layer** (`report.py`): Extends `Mt5DataClient` with reporting operations and export capabilities (`Mt5ReportClient`)

## Usage Guidelines

All modules follow these conventions:

- **Type Safety**: All functions include comprehensive type hints
- **Error Handling**: Centralized through `Mt5RuntimeError` with meaningful error messages
- **Documentation**: Google-style docstrings with examples
- **Validation**: Pydantic models for data validation and configuration
- **pandas Integration**: All data returns as DataFrames with proper datetime indexing

## Quick Start

```python
from pdmt5 import Mt5Client, Mt5Config, Mt5DataClient, Mt5ReportClient
import MetaTrader5 as mt5
from datetime import datetime

# Low-level API access with Mt5Client
with Mt5Client(mt5=mt5) as client:
    client.initialize()
    account = client.account_info()
    rates = client.copy_rates_from("EURUSD", mt5.TIMEFRAME_H1, datetime.now(), 100)

# Pandas-friendly interface with Mt5DataClient
config = Mt5Config(login=12345, password="pass", server="MetaQuotes-Demo")
with Mt5DataClient(mt5=mt5, config=config) as client:
    symbols_df = client.symbols_get()
    rates_df = client.copy_rates_from("EURUSD", mt5.TIMEFRAME_H1, datetime.now(), 100)

# Enhanced functionality with Mt5ReportClient
with Mt5ReportClient(mt5=mt5, config=config) as reporter:
    reporter.print_rates("EURUSD", timeframe="H1", count=10)
    reporter.export_rates_to_csv("EURUSD", "data.csv", timeframe="D1", count=100)
```

## Examples

See individual module pages for detailed usage examples and code samples.
