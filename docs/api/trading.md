# Trading

::: pdmt5.trading

## Overview

The trading module extends Mt5DataClient with advanced trading operations including position management, order execution, and dry run support for testing trading strategies without actual execution.

## Classes

### Mt5TradingClient
::: pdmt5.trading.Mt5TradingClient
    options:
      show_bases: false

Advanced trading client class that inherits from `Mt5DataClient` and provides specialized trading functionality.

### Mt5TradingError
::: pdmt5.trading.Mt5TradingError
    options:
      show_bases: false

Custom runtime exception for trading-specific errors.

## Usage Examples

### Basic Trading Operations

```python
import MetaTrader5 as mt5
from pdmt5 import Mt5TradingClient, Mt5Config

# Create configuration
config = Mt5Config(
    login=123456,
    password="your_password",
    server="broker_server",
    timeout=60000,
    portable=False
)

# Create client with dry run mode for testing
client = Mt5TradingClient(config=config, dry_run=True)

# Use as context manager
with client:
    # Get current positions as DataFrame
    positions_df = client.get_positions_as_df()
    print(f"Open positions: {len(positions_df)}")
    
    # Close positions for specific symbol
    results = client.close_open_positions("EURUSD")
    print(f"Closed positions: {results}")
```

### Production Trading

```python
# Create client for live trading (dry_run=False)
client = Mt5TradingClient(config=config, dry_run=False)

with client:
    # Close all positions for multiple symbols
    results = client.close_open_positions(["EURUSD", "GBPUSD", "USDJPY"])
    
    # Close all positions (all symbols)
    all_results = client.close_open_positions()
```

### Order Filling Modes

```python
# Configure different order filling modes
# IOC (Immediate or Cancel) - default
client_ioc = Mt5TradingClient(
    config=config, 
    order_filling_mode="IOC"
)

# FOK (Fill or Kill)
client_fok = Mt5TradingClient(
    config=config, 
    order_filling_mode="FOK"
)

# RETURN (Return if not filled)
client_return = Mt5TradingClient(
    config=config, 
    order_filling_mode="RETURN"
)
```

### Custom Order Parameters

```python
with client:
    # Close positions with custom parameters
    results = client.close_open_positions(
        "EURUSD",
        comment="Closing all EURUSD positions",
        deviation=10  # Maximum price deviation
    )
```

### Error Handling

```python
from pdmt5.trading import Mt5TradingError

try:
    with client:
        results = client.close_open_positions("EURUSD")
except Mt5TradingError as e:
    print(f"Trading error: {e}")
    # Handle specific trading errors
```

### Checking Order Status

```python
with client:
    # Check order (note: send_or_check_order is an internal method)
    # For trading operations, use the provided methods like close_open_positions
    
    # Example: Check if we can close a position
    positions = client.get_positions_as_df()
    if not positions.empty:
        # Close specific position
        results = client.close_open_positions("EURUSD")
```

## Position Management Features

The Mt5TradingClient provides intelligent position management:

- **Automatic Position Reversal**: Automatically determines the correct order type to close positions
- **Batch Operations**: Close multiple positions for one or more symbols
- **Dry Run Support**: Test trading logic without executing real trades
- **Flexible Filtering**: Close positions by symbol, group, or all positions
- **Custom Parameters**: Support for additional order parameters like comment, deviation, etc.

## Dry Run Mode

Dry run mode is essential for testing trading strategies:

```python
# Test mode - validates orders without execution
test_client = Mt5TradingClient(config=config, dry_run=True)

# Production mode - executes real orders
prod_client = Mt5TradingClient(config=config, dry_run=False)
```

In dry run mode:
- Orders are validated using `order_check()` instead of `order_send()`
- No actual trades are executed
- Full validation of margin requirements and order parameters
- Same return structure as live trading for easy testing

## Return Values

The `close_open_positions()` method returns a dictionary with symbols as keys:

```python
{
    "EURUSD": [
        {
            "retcode": 10009,  # Trade done
            "deal": 123456,
            "order": 789012,
            "volume": 1.0,
            "price": 1.1000,
            "comment": "Request executed",
            ...
        }
    ],
    "GBPUSD": [...]
}
```

## Best Practices

1. **Always use dry run mode first** to test your trading logic
2. **Handle Mt5TradingError exceptions** for proper error management
3. **Check return codes** to verify successful execution
4. **Use context managers** for automatic connection handling
5. **Log trading operations** for audit trails
6. **Validate positions exist** before attempting to close them
7. **Consider market hours** and trading session times

## Common Return Codes

- `TRADE_RETCODE_DONE` (10009): Trade operation completed successfully
- `TRADE_RETCODE_TRADE_DISABLED`: Trading disabled for the account
- `TRADE_RETCODE_MARKET_CLOSED`: Market is closed
- `TRADE_RETCODE_NO_MONEY`: Insufficient funds
- `TRADE_RETCODE_INVALID_VOLUME`: Invalid trade volume

## Integration with Mt5DataClient

Since Mt5TradingClient inherits from Mt5DataClient, all data retrieval methods are available:

```python
with Mt5TradingClient(config=config) as client:
    # Get current positions as DataFrame
    positions_df = client.get_positions_as_df()
    
    # Analyze positions
    if not positions_df.empty:
        # Calculate total exposure
        total_volume = positions_df['volume'].sum()
        
        # Close losing positions
        losing_positions = positions_df[positions_df['profit'] < 0]
        for symbol in losing_positions['symbol'].unique():
            client.close_open_positions(symbol)
```