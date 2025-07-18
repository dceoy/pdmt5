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
from pdmt5 import Mt5Config, Mt5DataClient, Mt5EtlClient

# Configure connection
config = Mt5Config(login=12345, password="pass", server="MetaQuotes-Demo")

# Use the data client
with Mt5DataClient(config) as client:
    # Get market data
    symbols = client.fetch_symbols()
    rates = client.fetch_rates("EURUSD", granularity="H1", count=100)

# Or use the printer for formatted output
with Mt5EtlClient(config) as printer:
    printer.print_rates("EURUSD", granularity="D1", count=10)
```

## Requirements

- Python 3.11+
- Windows OS (MetaTrader 5 requirement)
- MetaTrader 5 platform

## API Reference

Browse the API documentation to learn about available modules and functions:

- [Exception](api/exception.md) - Custom exception handling
- [DataFrame](api/dataframe.md) - Core data client and configuration
- [ETL](api/etl.md) - ETL operations and data export functionality

## Development

This project follows strict code quality standards:

- Type hints required (strict mode)
- Comprehensive linting with Ruff
- Test coverage tracking
- Google-style docstrings

## License

MIT License - see LICENSE file for details.