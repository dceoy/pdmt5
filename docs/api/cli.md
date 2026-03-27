# CLI Reference

The `pdmt5` command-line interface exports MetaTrader 5 data to CSV, JSON, Parquet, or SQLite3 files.

## Installation

The CLI is included with the pdmt5 package:

```bash
pip install pdmt5
```

After installation, the `pdmt5` command is available:

```bash
pdmt5 --help
```

You can also run it as a Python module:

```bash
python -m pdmt5 --help
```

## Global Options

All subcommands share these options, which must appear **before** the subcommand name:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `-o`, `--output` | `PATH` | Yes | Output file path. |
| `-f`, `--format` | `csv\|json\|parquet\|sqlite3` | No | Output format (auto-detected from extension if omitted). |
| `--table` | `TEXT` | No | Table name for SQLite3 output (default: `data`). |
| `--login` | `INT` | No | Trading account login. |
| `--password` | `TEXT` | No | Trading account password. |
| `--server` | `TEXT` | No | Trading server name. |
| `--path` | `TEXT` | No | Path to MetaTrader 5 terminal EXE file. |
| `--timeout` | `INT` | No | Connection timeout in milliseconds. |
| `--log-level` | `DEBUG\|INFO\|WARNING\|ERROR` | No | Logging level (default: `WARNING`). |

### Format Auto-Detection

When `--format` is omitted, the output format is inferred from the file extension:

| Extension | Format |
|-----------|--------|
| `.csv` | CSV |
| `.json` | JSON |
| `.parquet`, `.pq` | Parquet |
| `.db`, `.sqlite`, `.sqlite3` | SQLite3 |

## Subcommands

### Market Data

#### `rates-from`

Export OHLCV rates from a start date.

```bash
pdmt5 -o rates.csv rates-from \
  --symbol EURUSD --timeframe M1 \
  --date-from 2024-01-01 --count 1000
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--symbol` | `TEXT` | Yes | Symbol name. |
| `--timeframe` | `TIMEFRAME` | Yes | Timeframe (e.g., `M1`, `H1`, `D1`, or integer). |
| `--date-from` | `DATETIME` | Yes | Start date in ISO 8601 format. |
| `--count` | `INT` | Yes | Number of records. |

#### `rates-from-pos`

Export OHLCV rates from a bar position.

```bash
pdmt5 -o rates.json rates-from-pos \
  --symbol GBPUSD --timeframe H1 \
  --start-pos 0 --count 100
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--symbol` | `TEXT` | Yes | Symbol name. |
| `--timeframe` | `TIMEFRAME` | Yes | Timeframe. |
| `--start-pos` | `INT` | Yes | Start position (0 = current bar). |
| `--count` | `INT` | Yes | Number of records. |

#### `rates-range`

Export OHLCV rates for a date range.

```bash
pdmt5 -o rates.parquet rates-range \
  --symbol USDJPY --timeframe D1 \
  --date-from 2024-01-01 --date-to 2024-06-01
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--symbol` | `TEXT` | Yes | Symbol name. |
| `--timeframe` | `TIMEFRAME` | Yes | Timeframe. |
| `--date-from` | `DATETIME` | Yes | Start date. |
| `--date-to` | `DATETIME` | Yes | End date. |

#### `ticks-from`

Export tick data from a start date.

```bash
pdmt5 -o ticks.csv ticks-from \
  --symbol EURUSD --date-from 2024-01-01 \
  --count 5000 --flags ALL
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--symbol` | `TEXT` | Yes | Symbol name. |
| `--date-from` | `DATETIME` | Yes | Start date. |
| `--count` | `INT` | Yes | Number of ticks. |
| `--flags` | `FLAGS` | Yes | Tick flags (`ALL`, `INFO`, `TRADE`, or integer). |

#### `ticks-range`

Export tick data for a date range.

```bash
pdmt5 -o ticks.db ticks-range \
  --symbol EURUSD --date-from 2024-01-01 \
  --date-to 2024-02-01 --flags INFO
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--symbol` | `TEXT` | Yes | Symbol name. |
| `--date-from` | `DATETIME` | Yes | Start date. |
| `--date-to` | `DATETIME` | Yes | End date. |
| `--flags` | `FLAGS` | Yes | Tick flags. |

### Account & Terminal

#### `account-info`

Export trading account information.

```bash
pdmt5 -o account.json account-info
```

#### `terminal-info`

Export MetaTrader 5 terminal information.

```bash
pdmt5 -o terminal.csv terminal-info
```

### Symbols

#### `symbols`

Export the list of available symbols.

```bash
pdmt5 -o symbols.csv symbols --group "*USD*"
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--group` | `TEXT` | No | Symbol group filter (e.g., `*USD*`). |

#### `symbol-info`

Export detailed information for a single symbol.

```bash
pdmt5 -o eurusd.json symbol-info --symbol EURUSD
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--symbol` | `TEXT` | Yes | Symbol name. |

### Orders & Positions

#### `orders`

Export active (pending) orders.

```bash
pdmt5 -o orders.csv orders --symbol EURUSD
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--symbol` | `TEXT` | No | Symbol filter. |
| `--group` | `TEXT` | No | Group filter. |
| `--ticket` | `INT` | No | Ticket filter. |

#### `positions`

Export open positions.

```bash
pdmt5 -o positions.csv positions --group "*USD*"
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--symbol` | `TEXT` | No | Symbol filter. |
| `--group` | `TEXT` | No | Group filter. |
| `--ticket` | `INT` | No | Ticket filter. |

### History

#### `history-orders`

Export historical orders.

```bash
pdmt5 -o hist_orders.csv history-orders \
  --date-from 2024-01-01 --date-to 2024-06-01
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--date-from` | `DATETIME` | No | Start date. |
| `--date-to` | `DATETIME` | No | End date. |
| `--group` | `TEXT` | No | Group filter. |
| `--symbol` | `TEXT` | No | Symbol filter. |
| `--ticket` | `INT` | No | Order ticket. |
| `--position` | `INT` | No | Position ticket. |

#### `history-deals`

Export historical deals.

```bash
pdmt5 -o deals.parquet history-deals \
  --date-from 2024-01-01 --date-to 2024-06-01
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--date-from` | `DATETIME` | No | Start date. |
| `--date-to` | `DATETIME` | No | End date. |
| `--group` | `TEXT` | No | Group filter. |
| `--symbol` | `TEXT` | No | Symbol filter. |
| `--ticket` | `INT` | No | Order ticket. |
| `--position` | `INT` | No | Position ticket. |

## Custom Types

### `DATETIME`

ISO 8601 datetime strings. A UTC timezone is assumed when none is specified.

- `2024-01-15` (date only, interpreted as midnight UTC)
- `2024-01-15T12:00:00+00:00` (full datetime with timezone)

### `TIMEFRAME`

MetaTrader 5 timeframe names or integer values:

| Name | Value | Name | Value |
|------|-------|------|-------|
| `M1` | 1 | `H1` | 16385 |
| `M2` | 2 | `H2` | 16386 |
| `M3` | 3 | `H3` | 16387 |
| `M4` | 4 | `H4` | 16388 |
| `M5` | 5 | `H6` | 16390 |
| `M6` | 6 | `H8` | 16392 |
| `M10` | 10 | `H12` | 16396 |
| `M12` | 12 | `D1` | 16408 |
| `M15` | 15 | `W1` | 32769 |
| `M20` | 20 | `MN1` | 49153 |
| `M30` | 30 | | |

### `FLAGS`

Tick copy flags:

| Name | Value | Description |
|------|-------|-------------|
| `ALL` | 1 | All ticks. |
| `INFO` | 2 | Ticks with bid/ask changes. |
| `TRADE` | 4 | Ticks with last price and volume changes. |

## Public API

The `detect_format` and `export_dataframe` functions are also available as library imports:

::: pdmt5.cli.detect_format

::: pdmt5.cli.export_dataframe
