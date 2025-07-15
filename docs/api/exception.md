# Exception

::: pdmt5.exception

## Overview

The exception module provides custom exception handling for MetaTrader 5 runtime errors. It defines a specialized exception class that is raised when MetaTrader 5 operations fail.

## Classes

### Mt5RuntimeError
::: pdmt5.exception.Mt5RuntimeError
    options:
      show_bases: false

Custom runtime exception for MetaTrader 5 specific errors. This exception is raised throughout the pdmt5 package when MetaTrader 5 operations fail or return unexpected results.

## Usage Examples

### Basic Exception Handling

```python
from pdmt5 import Mt5DataClient, Mt5Config, Mt5RuntimeError
import MetaTrader5 as mt5

config = Mt5Config(login=12345, password="pass", server="MetaQuotes-Demo")
client = Mt5DataClient(mt5=mt5, config=config)

try:
    with client:
        # This might raise Mt5RuntimeError if symbol doesn't exist
        rates = client.copy_rates_from("INVALID_SYMBOL", mt5.TIMEFRAME_H1, datetime.now(), 100)
except Mt5RuntimeError as e:
    print(f"MetaTrader 5 error occurred: {e}")
    # Handle the error appropriately
```

### Common Error Scenarios

The `Mt5RuntimeError` is raised in various scenarios:

1. **Connection Failures**
   ```python
   try:
       client.initialize()
   except Mt5RuntimeError:
       print("Failed to connect to MetaTrader 5 terminal")
   ```

2. **Invalid Symbols**
   ```python
   try:
       tick = client.symbol_info_tick("NONEXISTENT")
   except Mt5RuntimeError:
       print("Symbol not found")
   ```

3. **Data Retrieval Failures**
   ```python
   try:
       rates = client.copy_rates_from("EURUSD", mt5.TIMEFRAME_M1, datetime(1990, 1, 1), 100)
   except Mt5RuntimeError:
       print("No data available for the specified period")
   ```

4. **Account Access Issues**
   ```python
   try:
       account = client.account_info()
   except Mt5RuntimeError:
       print("Failed to retrieve account information")
   ```

## Error Messages

The exception includes detailed error messages that typically contain:

- The MetaTrader 5 error code
- A descriptive error message
- Context about which operation failed

Example error message:
```
Mt5RuntimeError: Failed to get symbol info for 'INVALID': (-1, 'Unknown error')
```

## Best Practices

1. **Always wrap MT5 operations in try-except blocks** when error handling is important
2. **Log errors** for debugging and monitoring
3. **Provide user-friendly feedback** when errors occur
4. **Check for specific error conditions** if different handling is needed

```python
import logging

logger = logging.getLogger(__name__)

try:
    with client:
        result = client.positions_get()
except Mt5RuntimeError as e:
    logger.error(f"Failed to get positions: {e}")
    # Provide user feedback
    print("Unable to retrieve current positions. Please check your connection.")
    # Could also retry or take alternative action
```