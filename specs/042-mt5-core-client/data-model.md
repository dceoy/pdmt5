# Data Model: Mt5 Core Client

## Entities

### Mt5Client

- **Fields**: mt5 (MetaTrader5 module), logger (logging.Logger),
  \_is_initialized (bool)
- **Behavior**: Context manager for initialize/shutdown; wraps MT5 API calls

### TerminalSession

- **Fields**: initialized (bool), last_error (tuple[int, str])
- **Behavior**: Derived lifecycle state captured by Mt5Client initialization

### AccountInfo

- **Fields**: login, balance, leverage, server, currency
- **Behavior**: Returned from account_info retrieval as dict/DataFrame

### TerminalInfo

- **Fields**: name, company, build, path, community_account
- **Behavior**: Returned from terminal_info retrieval as dict/DataFrame

### SymbolInfo

- **Fields**: name, description, currency_base, currency_profit, trade_mode
- **Behavior**: Returned from symbol_info retrieval as dict/DataFrame

### TickData

- **Fields**: time, bid, ask, last, volume
- **Behavior**: Returned from symbol_info_tick and ticks retrieval

### RateData

- **Fields**: time, open, high, low, close, tick_volume, spread, real_volume
- **Behavior**: Returned from rates retrieval methods

### Order

- **Fields**: ticket, symbol, type, volume, price_open, time_setup
- **Behavior**: Returned from orders_get and history_orders_get

### Position

- **Fields**: ticket, symbol, type, volume, price_open, time
- **Behavior**: Returned from positions_get

### Deal

- **Fields**: ticket, order, symbol, volume, price, time
- **Behavior**: Returned from history_deals_get

## Relationships

- Mt5Client manages TerminalSession state and wraps MetaTrader5 API calls.
- Core MT5 data entities (AccountInfo, TerminalInfo, SymbolInfo, TickData,
  RateData, Order, Position, Deal) are produced by Mt5Client operations.
