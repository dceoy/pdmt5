# API Reference

This section contains the complete API documentation for pdmt5.

## Modules

The pdmt5 package consists of the following modules:

### [Mt5Client](mt5.md)

Base client class for MetaTrader 5 operations with connection management, low-level API access, and error handling (`Mt5RuntimeError`).

### [Mt5DataClient & Mt5Config](dataframe.md)

Core data client functionality and configuration, providing pandas-friendly interface to MetaTrader 5.

### [Constants](constants.md)

Canonical MT5 constant maps and parsers for timeframes, COPY_TICKS flags, and
ORDER_TYPE values. Use these helpers when CLI, HTTP, or validation layers need
to accept official names such as `TIMEFRAME_M1`, short aliases such as `M1`, or
integer values.

### [Mt5TradingClient](trading.md)

Direct order primitives around `order_check` / `order_send` and convenience
wrappers for common single-call patterns. Higher-level operational orchestration
belongs in `mt5cli`.

## Architecture Overview

### Internal package layers

1. **Base Layer** (`mt5.py`): `Mt5Client` — low-level MT5 API access and `Mt5RuntimeError`
2. **Data Layer** (`dataframe.py`): `Mt5DataClient` / `Mt5Config` — pandas-friendly interface and configuration
3. **Trading Layer** (`trading.py`): `Mt5TradingClient` — direct order primitives and convenience wrappers
4. **Constants** (`constants.py`): Canonical MT5 constant parsing and schema helpers
5. **Utilities** (`utils.py`): Time conversion and DataFrame helpers

### Ecosystem boundary

`pdmt5` is the **core MT5 / pandas adapter** and does not depend on any
downstream package. The table below shows where each concern belongs:

| Layer           | Package        | Responsibility                                                                                              |
| --------------- | -------------- | ----------------------------------------------------------------------------------------------------------- |
| Core adapter    | **pdmt5**      | MT5 lifecycle, low-level wrappers, DataFrame/dict helpers, constant parsing, minimal order primitives       |
| Operational SDK | **mt5cli**     | Margin-budget sizing, normalised execution results, broker pre-checks, batch workflows, CLI, SQLite history |
| HTTP adapter    | **mt5api**     | REST/FastAPI interface over `pdmt5`                                                                         |
| Strategy apps   | _(downstream)_ | Signal generation, risk policy, backtesting, optimisation, strategy-specific decisions                      |

## Usage Guidelines

All modules follow these conventions:

- **Type Safety**: All functions include comprehensive type hints
- **Error Handling**: Centralized through `Mt5RuntimeError` with meaningful error messages
- **Documentation**: Google-style docstrings with examples
- **Validation**: Pydantic models for data validation and configuration
- **pandas Integration**: Use `_as_df`/`_as_dict` helpers for pandas conversions
  (base methods return raw MT5 structures)

## Quick Start

```python
from pdmt5 import (
    Mt5Client,
    Mt5Config,
    Mt5DataClient,
    Mt5TradingClient,
    list_timeframe_names,
    list_timeframe_values,
    parse_copy_ticks,
    parse_timeframe,
)
import MetaTrader5 as mt5
from datetime import datetime

# Low-level API access with Mt5Client
with Mt5Client(mt5=mt5) as client:
    client.initialize()
    account = client.account_info()
    rates = client.copy_rates_from("EURUSD", mt5.TIMEFRAME_H1, datetime.now(), 100)

# Pandas-friendly interface with Mt5DataClient and configuration
config = Mt5Config(login=12345, password="pass", server="MetaQuotes-Demo")
with Mt5DataClient(mt5=mt5, config=config) as client:
    # Optional: login when credentials are provided
    client.login(config.login, config.password, config.server)
    symbols_df = client.symbols_get_as_df()
    rates_df = client.copy_rates_from_as_df(
        "EURUSD", parse_timeframe("H1"), datetime.now(), 100
    )

# Direct order primitives with Mt5TradingClient
with Mt5TradingClient(mt5=mt5, config=config) as client:
    # Place a market order (dry-run validates without executing)
    result = client.place_market_order("EURUSD", 0.1, "BUY", dry_run=True)

# Schema-friendly MT5 constant metadata
timeframe_names = list_timeframe_names()
timeframe_values = list_timeframe_values()
tick_flags = parse_copy_ticks("COPY_TICKS_ALL")
```

## Examples

See individual module pages for detailed usage examples and code samples.
