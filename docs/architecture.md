# Architecture contract

pdmt5 is a small adapter over the official `MetaTrader5` Python package. Direct
pdmt5 use is appropriate for low-level MT5 access. Application execution
workflows belong in `mt5cli` or the consuming application.

```text
mteor or another application
    -> mt5cli
        -> pdmt5
            -> MetaTrader5
```

## Stable package-root API

Only these names are stable package-root exports:

- `__version__`
- `Mt5Client`, `Mt5DataClient`, `Mt5Config`, `Mt5RuntimeError`
- `TIMEFRAME_MAP`, `COPY_TICKS_MAP`, `ORDER_TYPE_MAP`
- `parse_timeframe`, `parse_copy_ticks`, `parse_order_type`

Use `pdmt5.constants` for constant-name/value introspection helpers. Those
helpers are intentionally no longer re-exported from `pdmt5`; this keeps the
root API focused on client construction and canonical parsing.

The deliberately public module APIs are `pdmt5.mt5` (`Mt5Client`,
`Mt5RuntimeError`), `pdmt5.dataframe` (`Mt5Config`, `Mt5DataClient`), and the
explicit `pdmt5.constants.__all__`. `pdmt5.utils` is implementation-only.

## Owned low-level responsibilities

pdmt5 owns direct wrappers around official `MetaTrader5` functions, including
terminal initialization, login, shutdown, account and terminal access, market
data, market book, orders, positions, margin, profit, history, `order_check`,
and `order_send`. It owns `Mt5Config`, `Mt5RuntimeError`, canonical MT5
constants/parsers, and native-result conversion to dictionaries and pandas
DataFrames.

`Mt5Client` owns raw MT5 access and lifecycle primitives. Its context manager
initializes on entry and always shuts down on exit; failed initialization raises
`Mt5RuntimeError`. `Mt5DataClient` owns config-aware lifecycle: its context
manager initializes and logs in using `Mt5Config`, then shuts down on exit.

## Return shapes and errors

Raw `Mt5Client` methods return the native MT5 result (or the corresponding
scalar). `Mt5DataClient` methods ending in `_as_dict` return a single
dictionary, those ending in `_as_dicts` return a list of dictionaries, and
those ending in `_as_df` return a pandas `DataFrame`. DataFrame and dictionary
helpers convert MT5 time fields to timezone-naive trade-server timestamps by
default; pass `skip_to_datetime=True` where supported to retain raw epochs.

Invalid pdmt5 inputs, such as conflicting filters, invalid date ranges, or
non-positive counts, raise `ValueError`. An MT5 failure, including a `None`
response, failed initialization, or an underlying MT5 exception, raises
`Mt5RuntimeError` with MT5 error context.

## Explicit non-goals

pdmt5 does not construct market-order requests, select filling modes, size
positions from margin budgets, orchestrate position lifecycles, or implement
close, reversal, or retry workflows. It does not provide SQLite or other
persistence; CSV, JSON, Parquet, Grafana, or reporting workflows; command-line
or batch workflows; strategies, signals, risk thresholds, betting,
backtesting, or optimization. Put these policies and workflows in `mt5cli` or
the downstream application.

## Enforcement

Contract tests assert the root allowlist and module `__all__` declarations and
scan every production module for imports of `mt5cli` or `mteor`. Any new root
export, accidental module API, or reverse dependency fails CI.
