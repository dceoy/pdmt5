"""Command-line interface for pdmt5 data export."""

from __future__ import annotations

import argparse
import logging
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .dataframe import Mt5Config, Mt5DataClient

if TYPE_CHECKING:
    from collections.abc import Sequence

    import pandas as pd

logger = logging.getLogger(__name__)

TIMEFRAME_MAP: dict[str, int] = {
    "M1": 1,
    "M2": 2,
    "M3": 3,
    "M4": 4,
    "M5": 5,
    "M6": 6,
    "M10": 10,
    "M12": 12,
    "M15": 15,
    "M20": 20,
    "M30": 30,
    "H1": 16385,
    "H2": 16386,
    "H3": 16387,
    "H4": 16388,
    "H6": 16390,
    "H8": 16392,
    "H12": 16396,
    "D1": 16408,
    "W1": 32769,
    "MN1": 49153,
}

TICK_FLAG_MAP: dict[str, int] = {
    "ALL": 1,
    "INFO": 2,
    "TRADE": 4,
}

_FORMAT_EXTENSIONS: dict[str, str] = {
    ".csv": "csv",
    ".json": "json",
    ".parquet": "parquet",
    ".pq": "parquet",
    ".db": "sqlite3",
    ".sqlite": "sqlite3",
    ".sqlite3": "sqlite3",
}


def detect_format(
    output_path: Path,
    explicit_format: str | None = None,
) -> str:
    """Detect the output format from a file extension or explicit format string.

    Args:
        output_path: Path to the output file.
        explicit_format: Explicitly specified format, if any.

    Returns:
        The detected format string.

    Raises:
        ValueError: If the format cannot be determined.
    """
    if explicit_format is not None:
        return explicit_format
    suffix = output_path.suffix.lower()
    if suffix in _FORMAT_EXTENSIONS:
        return _FORMAT_EXTENSIONS[suffix]
    msg = (
        f"Cannot detect format from extension '{suffix}'."
        " Use --format to specify the output format."
    )
    raise ValueError(msg)


def export_dataframe(
    df: pd.DataFrame,
    output_path: Path,
    output_format: str,
    table_name: str = "data",
) -> None:
    """Export a pandas DataFrame to the specified file format.

    Args:
        df: DataFrame to export.
        output_path: Path to the output file.
        output_format: Output format (csv, json, parquet, or sqlite3).
        table_name: Table name for SQLite3 output.

    Raises:
        ValueError: If the output format is not supported.
    """
    if output_format == "csv":
        df.to_csv(output_path, index=False)
    elif output_format == "json":
        df.to_json(output_path, orient="records", date_format="iso", indent=2)
    elif output_format == "parquet":
        df.to_parquet(output_path, index=False)
    elif output_format == "sqlite3":
        with sqlite3.connect(output_path) as conn:
            df.to_sql(  # type: ignore[reportUnknownMemberType]
                table_name,
                conn,
                if_exists="replace",
                index=False,
            )
    else:
        msg = f"Unsupported output format: {output_format}"
        raise ValueError(msg)


def parse_datetime(value: str) -> datetime:
    """Parse an ISO 8601 datetime string to a timezone-aware datetime.

    Args:
        value: ISO 8601 datetime string (e.g., '2024-01-01' or
            '2024-01-01T12:00:00+00:00').

    Returns:
        Parsed datetime with UTC timezone if no timezone is specified.

    Raises:
        argparse.ArgumentTypeError: If the string cannot be parsed.
    """
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        msg = f"Invalid datetime format: '{value}'. Use ISO 8601 format."
        raise argparse.ArgumentTypeError(msg) from None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def parse_timeframe(value: str) -> int:
    """Parse a timeframe string or integer value.

    Args:
        value: Timeframe name (e.g., 'M1', 'H1', 'D1') or integer value.

    Returns:
        Integer timeframe value.

    Raises:
        argparse.ArgumentTypeError: If the timeframe is invalid.
    """
    upper = value.upper()
    if upper in TIMEFRAME_MAP:
        return TIMEFRAME_MAP[upper]
    try:
        return int(value)
    except ValueError:
        valid = ", ".join(TIMEFRAME_MAP)
        msg = f"Invalid timeframe: '{value}'. Use one of: {valid}, or an integer."
        raise argparse.ArgumentTypeError(msg) from None


def parse_tick_flags(value: str) -> int:
    """Parse tick flags string or integer value.

    Args:
        value: Tick flag name (ALL, INFO, TRADE) or integer value.

    Returns:
        Integer tick flag value.

    Raises:
        argparse.ArgumentTypeError: If the flag is invalid.
    """
    upper = value.upper()
    if upper in TICK_FLAG_MAP:
        return TICK_FLAG_MAP[upper]
    try:
        return int(value)
    except ValueError:
        valid = ", ".join(TICK_FLAG_MAP)
        msg = f"Invalid tick flags: '{value}'. Use one of: {valid}, or an integer."
        raise argparse.ArgumentTypeError(msg) from None


def _fetch_rates(
    client: Mt5DataClient,
    args: argparse.Namespace,
) -> pd.DataFrame:
    command: str = args.command
    if command == "rates-from":
        return client.copy_rates_from_as_df(
            symbol=args.symbol,
            timeframe=args.timeframe,
            date_from=args.date_from,
            count=args.count,
        )
    if command == "rates-from-pos":
        return client.copy_rates_from_pos_as_df(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_pos=args.start_pos,
            count=args.count,
        )
    return client.copy_rates_range_as_df(
        symbol=args.symbol,
        timeframe=args.timeframe,
        date_from=args.date_from,
        date_to=args.date_to,
    )


def _fetch_ticks(
    client: Mt5DataClient,
    args: argparse.Namespace,
) -> pd.DataFrame:
    if args.command == "ticks-from":
        return client.copy_ticks_from_as_df(
            symbol=args.symbol,
            date_from=args.date_from,
            count=args.count,
            flags=args.flags,
        )
    return client.copy_ticks_range_as_df(
        symbol=args.symbol,
        date_from=args.date_from,
        date_to=args.date_to,
        flags=args.flags,
    )


def _fetch_info(
    client: Mt5DataClient,
    args: argparse.Namespace,
) -> pd.DataFrame:
    command: str = args.command
    if command == "account-info":
        return client.account_info_as_df()
    if command == "terminal-info":
        return client.terminal_info_as_df()
    if command == "symbols":
        return client.symbols_get_as_df(group=args.group)
    return client.symbol_info_as_df(symbol=args.symbol)


def _fetch_trading(
    client: Mt5DataClient,
    args: argparse.Namespace,
) -> pd.DataFrame:
    command: str = args.command
    if command == "orders":
        return client.orders_get_as_df(
            symbol=args.symbol,
            group=args.group,
            ticket=args.ticket,
        )
    if command == "positions":
        return client.positions_get_as_df(
            symbol=args.symbol,
            group=args.group,
            ticket=args.ticket,
        )
    if command == "history-orders":
        return client.history_orders_get_as_df(
            date_from=args.date_from,
            date_to=args.date_to,
            group=args.group,
            symbol=args.symbol,
            ticket=args.ticket,
            position=args.position,
        )
    return client.history_deals_get_as_df(
        date_from=args.date_from,
        date_to=args.date_to,
        group=args.group,
        symbol=args.symbol,
        ticket=args.ticket,
        position=args.position,
    )


_RATES_COMMANDS = frozenset({"rates-from", "rates-from-pos", "rates-range"})
_TICKS_COMMANDS = frozenset({"ticks-from", "ticks-range"})
_INFO_COMMANDS = frozenset({"account-info", "terminal-info", "symbols", "symbol-info"})
_TRADING_COMMANDS = frozenset({
    "orders",
    "positions",
    "history-orders",
    "history-deals",
})


def fetch_data(
    client: Mt5DataClient,
    args: argparse.Namespace,
) -> pd.DataFrame:
    """Fetch data from MetaTrader5 based on the CLI subcommand.

    Args:
        client: MetaTrader5 data client.
        args: Parsed command-line arguments.

    Returns:
        DataFrame with the fetched data.

    Raises:
        ValueError: If the command is unknown.
    """
    command: str = args.command
    if command in _RATES_COMMANDS:
        return _fetch_rates(client, args)
    if command in _TICKS_COMMANDS:
        return _fetch_ticks(client, args)
    if command in _INFO_COMMANDS:
        return _fetch_info(client, args)
    if command in _TRADING_COMMANDS:
        return _fetch_trading(client, args)
    msg = f"Unknown command: {command}"
    raise ValueError(msg)


def _add_connection_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("connection")
    group.add_argument("--login", type=int, default=None, help="trading account login")
    group.add_argument("--password", default=None, help="trading account password")
    group.add_argument("--server", default=None, help="trading server name")
    group.add_argument(
        "--path", default=None, help="path to MetaTrader5 terminal EXE file"
    )
    group.add_argument(
        "--timeout", type=int, default=None, help="connection timeout in milliseconds"
    )


def _add_output_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("output")
    group.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="output file path",
    )
    group.add_argument(
        "-f",
        "--format",
        choices=("csv", "json", "parquet", "sqlite3"),
        default=None,
        help="output format (auto-detected from file extension if omitted)",
    )
    group.add_argument(
        "--table",
        default="data",
        help="table name for SQLite3 output (default: data)",
    )


def _add_symbol_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--symbol", required=True, help="symbol name (e.g., EURUSD)")


def _add_timeframe_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--timeframe",
        type=parse_timeframe,
        required=True,
        help="timeframe (e.g., M1, M5, H1, H4, D1, W1, MN1, or integer)",
    )


def _add_date_from_arg(
    parser: argparse.ArgumentParser,
    required: bool = True,
) -> None:
    parser.add_argument(
        "--date-from",
        type=parse_datetime,
        required=required,
        default=None,
        help="start date in ISO 8601 format (e.g., 2024-01-01)",
    )


def _add_date_to_arg(
    parser: argparse.ArgumentParser,
    required: bool = True,
) -> None:
    parser.add_argument(
        "--date-to",
        type=parse_datetime,
        required=required,
        default=None,
        help="end date in ISO 8601 format (e.g., 2024-02-01)",
    )


def _add_count_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--count", type=int, required=True, help="number of records to retrieve"
    )


def _add_flags_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--flags",
        type=parse_tick_flags,
        required=True,
        help="tick copy flags (ALL, INFO, TRADE, or integer)",
    )


def _add_filter_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--symbol", default=None, help="symbol filter")
    parser.add_argument("--group", default=None, help="group filter")
    parser.add_argument("--ticket", type=int, default=None, help="ticket filter")


def _add_history_args(parser: argparse.ArgumentParser) -> None:
    _add_date_from_arg(parser, required=False)
    _add_date_to_arg(parser, required=False)
    parser.add_argument("--group", default=None, help="group filter")
    parser.add_argument("--symbol", default=None, help="symbol filter")
    parser.add_argument("--ticket", type=int, default=None, help="order ticket")
    parser.add_argument("--position", type=int, default=None, help="position ticket")


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="pdmt5",
        description="Export MetaTrader5 data to CSV, JSON, Parquet, or SQLite3.",
    )
    _add_connection_args(parser)
    _add_output_args(parser)
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        default="WARNING",
        help="logging level (default: WARNING)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # rates-from
    p = subparsers.add_parser("rates-from", help="export rates from a start date")
    _add_symbol_arg(p)
    _add_timeframe_arg(p)
    _add_date_from_arg(p)
    _add_count_arg(p)

    # rates-from-pos
    p = subparsers.add_parser(
        "rates-from-pos", help="export rates from a start position"
    )
    _add_symbol_arg(p)
    _add_timeframe_arg(p)
    p.add_argument(
        "--start-pos", type=int, required=True, help="start position (0 = current bar)"
    )
    _add_count_arg(p)

    # rates-range
    p = subparsers.add_parser("rates-range", help="export rates for a date range")
    _add_symbol_arg(p)
    _add_timeframe_arg(p)
    _add_date_from_arg(p)
    _add_date_to_arg(p)

    # ticks-from
    p = subparsers.add_parser("ticks-from", help="export ticks from a start date")
    _add_symbol_arg(p)
    _add_date_from_arg(p)
    _add_count_arg(p)
    _add_flags_arg(p)

    # ticks-range
    p = subparsers.add_parser("ticks-range", help="export ticks for a date range")
    _add_symbol_arg(p)
    _add_date_from_arg(p)
    _add_date_to_arg(p)
    _add_flags_arg(p)

    # account-info
    subparsers.add_parser("account-info", help="export account information")

    # terminal-info
    subparsers.add_parser("terminal-info", help="export terminal information")

    # symbols
    p = subparsers.add_parser("symbols", help="export symbol list")
    p.add_argument("--group", default=None, help="symbol group filter (e.g., *USD*)")

    # symbol-info
    p = subparsers.add_parser("symbol-info", help="export symbol details")
    _add_symbol_arg(p)

    # orders
    p = subparsers.add_parser("orders", help="export active orders")
    _add_filter_args(p)

    # positions
    p = subparsers.add_parser("positions", help="export open positions")
    _add_filter_args(p)

    # history-orders
    p = subparsers.add_parser("history-orders", help="export historical orders")
    _add_history_args(p)

    # history-deals
    p = subparsers.add_parser("history-deals", help="export historical deals")
    _add_history_args(p)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Run the pdmt5 CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level))
    output_path: Path = args.output
    try:
        output_format = detect_format(output_path, args.format)
    except ValueError as e:
        parser.error(str(e))
    config = Mt5Config(
        path=args.path,
        login=args.login,
        password=args.password,
        server=args.server,
        timeout=args.timeout,
    )
    client = Mt5DataClient(config=config)
    client.initialize_and_login_mt5()
    try:
        df = fetch_data(client, args)
        export_dataframe(
            df=df,
            output_path=output_path,
            output_format=output_format,
            table_name=args.table,
        )
        logger.info("Exported %d rows to %s (%s)", len(df), output_path, output_format)
    finally:
        client.shutdown()
