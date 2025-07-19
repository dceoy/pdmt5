# pdmt5 API Documentation

Pandas-based data handler for MetaTrader 5 trading platform.

## Overview

pdmt5 is a Python library that provides a pandas-based interface for handling MetaTrader 5 trading data. It simplifies data manipulation and analysis tasks for financial trading applications.

## Features

- **MetaTrader 5 Integration**: Direct connection to MetaTrader 5 platform (Windows only)
- **Pandas-based**: Leverages pandas for efficient data manipulation
- **Type Safety**: Built with pydantic for robust data validation
- **Financial Focus**: Designed specifically for trading and financial data analysis

## Installation

```bash
pip install pdmt5
```

## Quick Start

```python
from pdmt5 import Mt5Client, Mt5Config, Mt5DataClient, Mt5ReportClient
import MetaTrader5 as mt5
from datetime import datetime

# Configure connection
config = Mt5Config(login=12345, password="pass", server="MetaQuotes-Demo")

# Low-level API access
with Mt5Client(mt5=mt5, config=config) as client:
    rates = client.copy_rates_from("EURUSD", mt5.TIMEFRAME_H1, datetime.now(), 100)

# Pandas-friendly interface
with Mt5DataClient(mt5=mt5, config=config) as client:
    symbols_df = client.symbols_get()
    rates_df = client.copy_rates_from("EURUSD", mt5.TIMEFRAME_H1, datetime.now(), 100)

# Enhanced functionality with reporting and export
with Mt5ReportClient(mt5=mt5, config=config) as reporter:
    reporter.print_rates("EURUSD", timeframe="H1", count=10)
    reporter.export_rates_to_csv("EURUSD", "data.csv", timeframe="D1", count=100)
```

## Requirements

- Python 3.11+
- Windows OS (MetaTrader 5 requirement)
- MetaTrader 5 platform

## API Reference

Browse the API documentation to learn about available modules and functions:

- [Mt5Client](api/mt5.md) - Base client for low-level MT5 API access and error handling
- [Mt5DataClient & Mt5Config](api/dataframe.md) - Pandas-friendly data client and configuration
- [Mt5ReportClient](api/report.md) - Reporting operations and data export functionality

## Development

This project follows strict code quality standards:

- Type hints required (strict mode)
- Comprehensive linting with Ruff
- Test coverage tracking
- Google-style docstrings

## License

MIT License - see LICENSE file for details.