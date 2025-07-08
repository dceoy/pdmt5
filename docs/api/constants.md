# Constants

::: pdmt5.constants

## Overview

The constants module provides comprehensive enumeration classes for MetaTrader 5 trading platform constants. These enums ensure type safety and provide meaningful names for numeric constants used throughout the MetaTrader 5 API.

## Enums

### Timeframe
::: pdmt5.constants.Timeframe
    options:
      show_bases: false
      show_source: false

### Order Management
::: pdmt5.constants.OrderType
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.OrderState
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.OrderFilling
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.OrderTime
    options:
      show_bases: false
      show_source: false

### Trading Operations
::: pdmt5.constants.TradeAction
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.PositionType
    options:
      show_bases: false
      show_source: false

### Deal Information
::: pdmt5.constants.DealType
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.DealEntry
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.DealReason
    options:
      show_bases: false
      show_source: false

### Symbol Properties
::: pdmt5.constants.SymbolCalcMode
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.SymbolTradeMode
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.SymbolOrderMode
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.SymbolFillMode
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.SymbolExpiration
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.SymbolSwapMode
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.SymbolOption
    options:
      show_bases: false
      show_source: false

::: pdmt5.constants.SymbolOptionRight
    options:
      show_bases: false
      show_source: false

### Tick Data
::: pdmt5.constants.TickFlag
    options:
      show_bases: false
      show_source: false

## Usage Examples

```python
from pdmt5.constants import Timeframe, OrderType, TickFlag

# Using timeframe constants
timeframe = Timeframe.H1  # 1-hour timeframe
daily_tf = Timeframe.D1   # Daily timeframe

# Using order type constants
buy_order = OrderType.BUY
sell_limit = OrderType.SELL_LIMIT

# Using tick flag constants
all_ticks = TickFlag.ALL
bid_ticks = TickFlag.BID
```

## Notes

- All enums inherit from `IntEnum` for compatibility with MetaTrader 5 API
- Values correspond exactly to MetaTrader 5 platform constants
- Use these enums instead of raw integers for better code readability and type safety