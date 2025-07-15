# API Reference

This section contains the complete API documentation for pdmt5.

## Modules

The pdmt5 package consists of the following modules:

### [Exception](exception.md)
Custom exception handling for MetaTrader 5 runtime errors.

### [Manipulator](manipulator.md)
Core data client functionality providing pandas-friendly interface to MetaTrader 5.

### [Printer](printer.md)
Pretty printing and data export functionality for MetaTrader 5 data.

## Architecture Overview

The package follows a layered architecture:

1. **Exception Layer** (`exception.py`): Defines custom exceptions for MT5-specific errors
2. **Core Layer** (`manipulator.py`): Provides the base `Mt5DataClient` class with all MT5 interactions
3. **Presentation Layer** (`printer.py`): Extends `Mt5DataClient` with formatting and export capabilities

## Usage Guidelines

All modules follow these conventions:

- **Type Safety**: All functions include comprehensive type hints
- **Error Handling**: Centralized through `Mt5RuntimeError` with meaningful error messages
- **Documentation**: Google-style docstrings with examples
- **Validation**: Pydantic models for data validation and configuration
- **pandas Integration**: All data returns as DataFrames with proper datetime indexing

## Quick Start

```python
from pdmt5 import Mt5Config, Mt5DataClient, Mt5DataPrinter

# Basic usage with Mt5DataClient
config = Mt5Config(login=12345, password="pass", server="MetaQuotes-Demo")
with Mt5DataClient(config) as client:
    symbols = client.fetch_symbols()
    rates = client.fetch_rates("EURUSD", timeframe="H1", count=100)

# Enhanced functionality with Mt5DataPrinter
with Mt5DataPrinter(config) as printer:
    printer.print_rates("EURUSD", timeframe="D1", count=10)
    printer.export_rates_to_csv("EURUSD", "data/eurusd.csv")
```

## Examples

See individual module pages for detailed usage examples and code samples.