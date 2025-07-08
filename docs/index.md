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
import pdmt5

# Your trading data manipulation code here
```

## Requirements

- Python 3.11+
- Windows OS (MetaTrader 5 requirement)
- MetaTrader 5 platform

## API Reference

Browse the API documentation to learn about available modules and functions:

- [Constants](api/constants.md) - Configuration constants and enums
- [Manipulator](api/manipulator.md) - Core data manipulation functionality

## Development

This project follows strict code quality standards:

- Type hints required (strict mode)
- Comprehensive linting with Ruff
- Test coverage tracking
- Google-style docstrings

## License

MIT License - see LICENSE file for details.