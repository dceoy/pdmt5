# Data Model: MT5 client operations

## Entities

### Mt5Config

- **Fields**: path (str|None), login (int|None), password (str|None),
  server (str|None), timeout (int|None)
- **Validation**: Frozen pydantic model; optional values; timeout in milliseconds

### Mt5Client

- **Fields**: mt5 (MetaTrader5 module), logger (logging.Logger),
  \_is_initialized (bool)
- **Behavior**: Context manager for initialize/shutdown; wraps MT5 API calls

### Mt5DataClient

- **Extends**: Mt5Client
- **Fields**: config (Mt5Config), retry_count (int >= 0)
- **Behavior**: Converts MT5 responses into dicts/DataFrames with optional
  datetime conversion and index setting

### Mt5TradingClient

- **Extends**: Mt5DataClient
- **Fields**: cached retcode sets (successful, failed)
- **Behavior**: Sends/checks orders, closes positions, updates SL/TP, and
  calculates trading metrics

### TradingRequest

- **Fields**: action, symbol, volume, type, type_filling, type_time, position,
  sl, tp, plus extra MT5 request parameters
- **Behavior**: Encapsulates order check/send/close requests

### TradingResult

- **Fields**: retcode, comment, request payload, and MT5 response attributes
- **Behavior**: Returned as dicts or DataFrames from order operations

### PositionMetrics

- **Fields**: elapsed_seconds, margin, signed_margin, signed_volume,
  underlier_profit_ratio
- **Behavior**: Derived from positions and symbol tick data

## Relationships

- Mt5DataClient composes Mt5Config and extends Mt5Client.
- Mt5TradingClient extends Mt5DataClient and consumes TradingRequest objects.
- TradingResult is produced by trading operations and may embed the request.
- PositionMetrics are derived from Mt5DataClient position data and symbol info.
