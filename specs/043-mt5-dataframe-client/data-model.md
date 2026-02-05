# Data Model: Mt5 DataFrame Client

## Entities

### Mt5Config

- **Fields**: path (str|None), login (int|None), password (str|None),
  server (str|None), timeout (int|None)
- **Validation**: Frozen pydantic model; optional values; timeout in milliseconds

### Mt5DataClient

- **Extends**: Mt5Client
- **Fields**: config (Mt5Config), retry_count (int >= 0)
- **Behavior**: Converts MT5 responses into dicts/DataFrames with optional
  datetime conversion and index setting

### DataFrameResult

- **Fields**: pandas.DataFrame with MT5 schema columns per response type
- **Behavior**: Empty DataFrame returned when MT5 returns no data

### RateSeries

- **Fields**: time, open, high, low, close, tick_volume, spread, real_volume
- **Behavior**: Returned from rates DataFrame helpers

### TickSeries

- **Fields**: time, bid, ask, last, volume
- **Behavior**: Returned from ticks DataFrame helpers

### AccountSnapshot

- **Fields**: login, balance, leverage, currency
- **Behavior**: Returned from account_info_as_df

### SymbolSnapshot

- **Fields**: name, description, currency_base, currency_profit, trade_mode
- **Behavior**: Returned from symbol_info_as_df and symbols_get_as_df

## Relationships

- Mt5DataClient composes Mt5Config and extends Mt5Client.
- DataFrameResult objects are produced by MT5 dict responses with conversion.
- RateSeries and TickSeries are DataFrameResult specializations.
