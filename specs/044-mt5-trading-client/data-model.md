# Data Model: Mt5 Trading Client

## Entities

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

### ClosePositionsRequest

- **Fields**: symbols, order_filling_mode, dry_run
- **Behavior**: Defines batch close operations for positions

### MarketOrderRequest

- **Fields**: symbol, volume, order_side, order_filling_mode, order_time_mode,
  dry_run
- **Behavior**: Defines market order placement parameters

### SltpUpdateRequest

- **Fields**: symbol, stop_loss, take_profit, tickets, dry_run
- **Behavior**: Defines stop-loss/take-profit update parameters

### PositionMetrics

- **Fields**: elapsed_seconds, margin, signed_margin, signed_volume,
  underlier_profit_ratio
- **Behavior**: Derived from positions and symbol tick data

## Relationships

- Mt5TradingClient extends Mt5DataClient and consumes TradingRequest objects.
- TradingResult is produced by trading operations and may embed the request.
- PositionMetrics are derived from Mt5TradingClient position data and symbol info.
