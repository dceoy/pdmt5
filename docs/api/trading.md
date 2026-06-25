# Trading

::: pdmt5.trading

## Overview

The trading module extends `Mt5DataClient` with direct order primitives around
`order_check` / `order_send` and convenience wrappers for common single-call patterns.

### Responsibility boundary

`pdmt5` is the **core MT5 / pandas adapter**. Its scope covers the MT5 connection
lifecycle, low-level MT5 method wrappers, DataFrame / dict conversion helpers,
canonical MT5 constant parsing, and minimal direct order primitives.

Generic operational orchestration — margin-budget sizing, normalised
execution-result handling, broker constraint pre-checks, and downstream trading
workflows — belongs in **`mt5cli`**, the canonical downstream operational SDK /
CLI / batch / SQLite history layer built on top of `pdmt5`.

`mt5api` is the sibling HTTP/FastAPI adapter that exposes `pdmt5` over a REST
interface. Downstream strategy applications own signal generation, risk policy,
backtesting, optimisation, and strategy-specific order decisions.

### Method classification

Methods in `Mt5TradingClient` fall into two categories:

- **Core MT5 primitive**: thin wrapper or constant mapping directly over the
  MetaTrader5 Python API. Always appropriate in `pdmt5`.
- **Convenience wrapper**: slightly higher-level helper that remains closely
  coupled to a single MT5 call and is appropriate in `pdmt5`.

See the docstring of each method for its individual classification.

## Classes

### Mt5TradingClient

::: pdmt5.trading.Mt5TradingClient
options:
show_bases: false

Trading client that extends `Mt5DataClient` with direct order primitives
(`place_market_order`, `_send_or_check_order`) and convenience wrappers
(`calculate_minimum_order_margin`, `fetch_latest_rates_as_df`,
`fetch_latest_ticks_as_df`). Higher-level operational orchestration belongs in
`mt5cli`.

### Mt5TradingError

::: pdmt5.trading.Mt5TradingError
options:
show_bases: false

Custom runtime exception for trading-specific errors.

## Usage Examples

### Market Order Placement

Place market orders with flexible configuration:

```python
from pdmt5 import Mt5TradingClient, Mt5Config

config = Mt5Config(
    login=123456,
    password="your_password",
    server="broker_server",
    timeout=60000,
)

with Mt5TradingClient(config=config) as client:
    # Place a BUY market order
    result = client.place_market_order(
        symbol="EURUSD",
        volume=1.0,
        order_side="BUY",
        order_filling_mode="IOC",  # Immediate or Cancel
        order_time_mode="GTC",     # Good Till Cancelled
        dry_run=False,             # Set to True for testing
        comment="My buy order"
    )

    # Place a SELL market order with FOK filling
    result = client.place_market_order(
        symbol="EURUSD",
        volume=0.5,
        order_side="SELL",
        order_filling_mode="FOK",  # Fill or Kill
        dry_run=True  # Test mode
    )

    print(f"Order result: {result}")
```

### Error Handling

```python
from pdmt5.trading import Mt5TradingError

try:
    with Mt5TradingClient(config=config) as client:
        result = client.place_market_order("EURUSD", 1.0, "BUY", raise_on_error=True)
except Mt5TradingError as e:
    print(f"Trading error: {e}")
```

## Dry Run Mode

Dry run mode validates orders without executing real trades:

```python
with Mt5TradingClient(config=config) as client:
    # Validates the order request via order_check() without sending it
    result = client.place_market_order(
        symbol="EURUSD",
        volume=0.1,
        order_side="BUY",
        dry_run=True,
    )
```

In dry run mode:

- Orders are validated using `order_check()` instead of `order_send()`
- No actual trades are executed
- Full validation of margin requirements and order parameters
- Same return structure as live trading for easy testing

## Common Return Codes

- `TRADE_RETCODE_DONE` (10009): Trade operation completed successfully
- `TRADE_RETCODE_TRADE_DISABLED`: Trading disabled for the account
- `TRADE_RETCODE_MARKET_CLOSED`: Market is closed
- `TRADE_RETCODE_NO_MONEY`: Insufficient funds
- `TRADE_RETCODE_INVALID_VOLUME`: Invalid trade volume

## Margin Calculation

`calculate_minimum_order_margin` is a **convenience wrapper** over
`order_calc_margin` that returns the margin required for the broker's minimum
allowable volume.

```python
with Mt5TradingClient(config=config) as client:
    # Calculate minimum margin required for BUY order
    min_margin_buy = client.calculate_minimum_order_margin("EURUSD", "BUY")
    print(f"Minimum volume: {min_margin_buy['volume']}")
    print(f"Minimum margin: {min_margin_buy['margin']}")

    # Calculate minimum margin required for SELL order
    min_margin_sell = client.calculate_minimum_order_margin("EURUSD", "SELL")
```

## Market Data Methods

`fetch_latest_rates_as_df` and `fetch_latest_ticks_as_df` are **convenience
wrappers** appropriate in `pdmt5`.

### OHLC Data Retrieval

```python
with Mt5TradingClient(config=config) as client:
    # Fetch latest rate data as DataFrame
    rates_df = client.fetch_latest_rates_as_df(
        symbol="EURUSD",
        granularity="M1",  # 1-minute bars
        count=1440,        # Last 24 hours
        index_keys="time"
    )
    print(f"Latest rates: {rates_df.tail()}")
```

### Tick Data Analysis

```python
with Mt5TradingClient(config=config) as client:
    # Fetch recent tick data
    ticks_df = client.fetch_latest_ticks_as_df(
        symbol="EURUSD",
        seconds=300,           # Last 5 minutes
        index_keys="time_msc"
    )
    print(f"Tick count: {len(ticks_df)}")
```
