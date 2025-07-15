"""MetaTrader5 data client with pretty printing capabilities."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd

from .manipulator import Mt5DataClient


class Mt5DataPrinter(Mt5DataClient):
    """MetaTrader5 data client with pretty printing capabilities.

    This class extends Mt5DataClient to provide methods for pretty-printing
    DataFrames and other data structures.
    """

    @staticmethod
    def print_json(
        data: dict[str, Any] | list[Any] | str | float | bool | None,
        indent: int = 2,
    ) -> None:
        """Print data as formatted JSON.

        Args:
            data: Data to serialize and print.
            indent: JSON indentation level.
        """
        print(json.dumps(data, indent=indent))  # noqa: T201

    @staticmethod
    def print_df(
        df: pd.DataFrame,
        display_max_columns: int = 500,
        display_width: int = 1500,
    ) -> None:
        """Displays DataFrame with custom formatting options.

        Args:
            df: DataFrame to display and export.
            display_max_columns: Maximum columns to display.
            display_width: Display width in characters.
        """
        pd.set_option("display.max_columns", display_max_columns)
        pd.set_option("display.width", display_width)
        pd.set_option("display.max_rows", df.shape[0])
        print(df.reset_index().to_string(index=False))  # noqa: T201

    @staticmethod
    def drop_duplicates_in_sqlite3(
        cursor: sqlite3.Cursor, table: str, ids: list[str]
    ) -> None:
        """Remove duplicate rows from SQLite table.

        Removes duplicate rows based on specified ID columns, keeping
        only the first occurrence (minimum ROWID).

        Args:
            cursor: SQLite database cursor.
            table: Table name to deduplicate.
            ids: Column names to use for duplicate detection.
        """
        cursor.execute(
            (
                "DELETE FROM {table} WHERE ROWID NOT IN"  # noqa: RUF027
                " (SELECT MIN(ROWID) FROM {table} GROUP BY {ids_str})"
            ),
            {"table": table, "ids_str": ", ".join(f'"{i}"' for i in ids)},
        )

    def export_df(
        self,
        df: pd.DataFrame,
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
        sqlite3_table: str | None = None,
    ) -> None:
        """Export DataFrame to CSV or SQLite3 database.

        Args:
            df: DataFrame to display and export.
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite database (requires sqlite3_table).
            sqlite3_table: Table name for SQLite export.
        """
        self.logger.debug("df.shape: %s", df.shape)
        self.logger.debug("df.dtypes: %s", df.dtypes)
        self.logger.debug("df: %s", df)
        if csv_path:
            self.logger.info("Write CSV data: %s", csv_path)
            df.to_csv(csv_path)
        elif sqlite3_path and sqlite3_table:
            self.logger.info(
                "Save data with SQLite3: %s => %s", sqlite3_table, sqlite3_path
            )
            with sqlite3.connect(sqlite3_path) as c:
                df.to_sql(sqlite3_table, c, if_exists="append")
                self.drop_duplicates_in_sqlite3(
                    cursor=c.cursor(),
                    table=sqlite3_table,
                    ids=[str(name) for name in df.index.names],
                )

    def print_deals(
        self,
        hours: float,
        date_to: str | None = None,
        group: str | None = None,
    ) -> None:
        """Print trading deals from history.

        Retrieves and displays historical trading deals within a specified
        time window, optionally filtered by symbol group.

        Args:
            hours: Number of hours to look back from end date.
            date_to: End date for history search (defaults to now).
            group: Symbol group filter (optional).
        """
        self.logger.info("hours: %s, date_to: %s, group: %s", hours, date_to, group)
        end_date = pd.to_datetime(date_to) if date_to else datetime.now(UTC)
        self.logger.info("end_date: %s", end_date)
        deals = self.mt5.history_deals_get(
            (end_date - timedelta(hours=float(hours))),
            end_date,
            **({"group": group} if group else {}),
        )
        self.logger.debug("deals: %s", deals)
        self.print_json([d._asdict() for d in deals])

    def print_orders(self) -> None:
        """Print current active orders.

        Retrieves and displays all currently active pending orders.
        """
        orders = self.mt5.orders_get()
        self.logger.debug("orders: %s", orders)
        self.print_json([o._asdict() for o in orders])

    def print_positions(self) -> None:
        """Print current open positions.

        Retrieves and displays all currently open trading positions.
        """
        positions = self.mt5.positions_get()
        self.logger.debug("positions: %s", positions)
        self.print_json([p._asdict() for p in positions])

    def print_margins(self, symbol: str) -> None:
        """Print margin requirements for a symbol.

        Calculates and displays minimum margin requirements for buy and sell
        orders of the specified financial instrument.

        Args:
            symbol: Financial instrument symbol (e.g., 'EURUSD').
        """
        self.logger.info("symbol: %s", symbol)
        account_currency = self.mt5.account_info().currency
        self.logger.info("account_currency: %s", account_currency)
        volume_min = self.mt5.symbol_info(symbol).volume_min
        self.logger.info("volume_min: %s", volume_min)
        symbol_info_tick = self.mt5.symbol_info_tick(symbol)
        self.logger.debug("symbol_info_tick: %s", symbol_info_tick)
        ask_margin = self.mt5.order_calc_margin(
            self.mt5.ORDER_TYPE_BUY, symbol, volume_min, symbol_info_tick.ask
        )
        self.logger.info("ask_margin: %s", ask_margin)
        bid_margin = self.mt5.order_calc_margin(
            self.mt5.ORDER_TYPE_SELL, symbol, volume_min, symbol_info_tick.bid
        )
        self.logger.info("bid_margin: %s", bid_margin)
        self.print_json({
            "symbol": symbol,
            "account_currency": account_currency,
            "volume": volume_min,
            "margin": {"ask": ask_margin, "bid": bid_margin},
        })

    def print_ticks(
        self,
        symbol: str,
        seconds: float,
        date_to: str | None = None,
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print tick data for a symbol.

        Retrieves and displays tick-level price data for the specified symbol
        within a time window. Optionally exports data to CSV or SQLite.

        Args:
            symbol: Financial instrument symbol.
            seconds: Number of seconds of tick data to fetch.
            date_to: End date for data (defaults to latest tick time).
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite export (optional).
        """
        self.logger.info(
            "symbol: %s, seconds: %s, date_to: %s, csv_path: %s",
            symbol,
            seconds,
            date_to,
            csv_path,
        )
        df_tick = self._fetch_df_tick(
            symbol=symbol, seconds=float(seconds), date_to=date_to
        )
        self.print_df(df=df_tick)
        self.export_df(
            df=df_tick,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table=f"tick_{symbol}",
        )

    def _fetch_df_tick(
        self,
        symbol: str,
        seconds: float,
        date_to: str | None = None,
    ) -> pd.DataFrame:
        """Fetch tick data as DataFrame.

        Retrieves tick data from MetaTrader 5 and converts it to a pandas
        DataFrame with proper datetime indexing.

        Args:
            symbol: Financial instrument symbol.
            seconds: Number of seconds of data to fetch.
            date_to: End date for data (optional).

        Returns:
            pd.DataFrame: Tick data with time index.
        """
        delta = timedelta(seconds=seconds)
        if date_to:
            end_date = pd.to_datetime(date_to)
            start_date = end_date - delta
        else:
            symbol_info_tick = self.mt5.symbol_info_tick(symbol)
            self.logger.debug("symbol_info_tick: %s", symbol_info_tick)
            last_tick_time = pd.to_datetime(symbol_info_tick.time, unit="s")
            end_date = last_tick_time + delta
            start_date = last_tick_time - delta
        self.logger.info("start_date: %s, end_date: %s", start_date, end_date)
        ticks = self.mt5.copy_ticks_range(
            symbol, start_date, end_date, self.mt5.COPY_TICKS_ALL
        )
        self.logger.debug("ticks: %s", ticks)
        return (
            pd.DataFrame(ticks)
            .assign(
                time=lambda d: pd.to_datetime(d["time"], unit="s"),
                time_msc=lambda d: pd.to_datetime(d["time_msc"], unit="ms"),
            )
            .set_index(["time", "time_msc"])
        )

    def print_rates(
        self,
        symbol: str,
        granularity: str,
        count: int,
        start_pos: int = 0,
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print OHLC rate data for a symbol.

        Retrieves and displays candlestick (OHLC) data for the specified symbol
        at a given time granularity. Optionally exports data to CSV or SQLite.

        Args:
            symbol: Financial instrument symbol.
            granularity: Time granularity (e.g., 'M1', 'H1', 'D1').
            count: Number of bars to fetch.
            start_pos: Starting position (0 = most recent).
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite export (optional).
        """
        self.logger.info(
            "symbol: %s, granularity: %s, count: %s, start_pos: %s, csv_path: %s",
            symbol,
            granularity,
            count,
            start_pos,
            csv_path,
        )
        df_rate = self._fetch_df_rate(
            symbol=symbol,
            granularity=granularity,
            count=count,
            start_pos=start_pos,
        )
        self.print_df(df=df_rate)
        self.export_df(
            df=df_rate,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table=f"rate_{symbol}",
        )

    def _fetch_df_rate(
        self, symbol: str, granularity: str, count: int, start_pos: int = 0
    ) -> pd.DataFrame:
        """Fetch OHLC rate data as DataFrame.

        Retrieves rate data from MetaTrader 5 and converts it to a pandas
        DataFrame with proper datetime indexing.

        Args:
            symbol: Financial instrument symbol.
            granularity: Time granularity.
            count: Number of bars to fetch.
            start_pos: Starting position.

        Returns:
            pd.DataFrame: OHLC rate data with time index.
        """
        timeframe = getattr(self.mt5, f"TIMEFRAME_{granularity}")
        self.logger.info("MetaTrader5.TIMEFRAME_%s: %s", granularity, timeframe)
        rates = self.mt5.copy_rates_from_pos(symbol, timeframe, start_pos, int(count))
        self.logger.debug("rates: %s", rates)
        return (
            pd.DataFrame(rates)
            .assign(time=lambda d: pd.to_datetime(d["time"], unit="s"))
            .set_index("time")
        )

    def print_symbol_info(self, symbol: str) -> None:
        """Print detailed information about a financial instrument.

        Retrieves and displays symbol specifications and current tick data
        for the specified financial instrument.

        Args:
            symbol: Financial instrument symbol.
        """
        self.logger.info("symbol: %s", symbol)
        symbol_info = self.mt5.symbol_info(symbol)
        self.logger.debug("symbol_info: %s", symbol_info)
        symbol_info_tick = self.mt5.symbol_info_tick(symbol)
        self.logger.debug("symbol_info_tick: %s", symbol_info_tick)
        self.print_json({
            "symbol": symbol,
            "info": symbol_info._asdict(),
            "tick": symbol_info_tick._asdict(),
        })

    def print_mt5_info(self) -> None:
        """Print MetaTrader 5 terminal and account information.

        Displays MetaTrader 5 version, terminal status and settings,
        trading account information, and available instrument count.
        """
        self.logger.info("MetaTrader5.__version__: %s", self.mt5.__version__)
        self.logger.info("MetaTrader5.__author__: %s", self.mt5.__author__)
        terminal_version = self.mt5.version()
        self.logger.debug("terminal_version: %s", terminal_version)
        print(  # noqa: T201
            os.linesep.join([
                f"{k}: {v}"
                for k, v in zip(
                    [
                        "MetaTrader 5 terminal version",
                        "Build",
                        "Build release date",
                    ],
                    terminal_version,
                    strict=False,
                )
            ])
        )
        terminal_info = self.mt5.terminal_info()
        self.logger.debug("terminal_info: %s", terminal_info)
        print(  # noqa: T201
            f"Terminal status and settings:{os.linesep}"
            + os.linesep.join([
                f"  {k}: {v}" for k, v in terminal_info._asdict().items()
            ])
        )
        account_info = self.mt5.account_info()
        self.logger.debug("account_info: %s", account_info)
        print(  # noqa: T201
            f"Trading account info:{os.linesep}"
            + os.linesep.join([
                f"  {k}: {v}" for k, v in account_info._asdict().items()
            ])
        )
        print(f"Number of financial instruments: {self.mt5.symbols_total()}")  # noqa: T201
