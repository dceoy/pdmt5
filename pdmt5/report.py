"""MetaTrader5 data client with reporting capabilities."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import pandas as pd

from .dataframe import Mt5DataClient


class Mt5ReportClient(Mt5DataClient):
    """MetaTrader5 data client with reporting capabilities.

    This class extends Mt5DataClient to provide methods for
    printing and exporting MetaTrader 5 data.
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
        include_index: bool = True,
        display_max_columns: int = 500,
        display_width: int = 1500,
    ) -> None:
        """Displays DataFrame with custom formatting options.

        Args:
            df: DataFrame to display and export.
            include_index: Whether to include DataFrame index in output.
            display_max_columns: Maximum columns to display.
            display_width: Display width in characters.
        """
        pd.set_option("display.max_columns", display_max_columns)
        pd.set_option("display.width", display_width)
        pd.set_option("display.max_rows", df.shape[0])
        print(df.reset_index().to_string(index=include_index))  # noqa: T201

    @staticmethod
    def drop_duplicates_in_sqlite3(
        cursor: sqlite3.Cursor,
        table: str,
        ids: list[str],
    ) -> None:
        """Remove duplicate rows from SQLite3 table.

        Removes duplicate rows based on specified ID columns, keeping
        only the first occurrence (minimum ROWID).

        Args:
            cursor: SQLite3 cursor for executing SQL commands.
            table: Table name to deduplicate.
            ids: Column names to use for duplicate detection.

        Raises:
            ValueError: If table or column names are invalid.
        """
        if not table.isidentifier():
            error_message = f"Invalid table name: {table}"
            raise ValueError(error_message)
        elif {i for i in ids if not i.isidentifier()}:
            error_message = f"Invalid column names: {', '.join(ids)}"
            raise ValueError(error_message)
        else:
            ids_csv = ", ".join(f'"{i}"' for i in ids)
            cursor.execute(
                f"DELETE FROM {table} WHERE ROWID NOT IN"  # noqa: S608
                f" (SELECT MIN(ROWID) FROM {table} GROUP BY {ids_csv})"
            )

    def write_df_to_sqlite3(
        self,
        df: pd.DataFrame,
        sqlite3_file_path: str,
        table: str,
        if_exists: Literal["fail", "replace", "append"] = "append",
        index: bool = True,
        drop_duplicates: bool = True,
    ) -> None:
        """Write data frame records to SQLite3 table.

        Args:
            df: DataFrame to write.
            sqlite3_file_path: Path to SQLite3 database file.
            table: Table name to write DataFrame to.
            if_exists: Action if table already exists ('fail', 'replace', 'append').
            index: Whether to write DataFrame index as a column.
            drop_duplicates: Whether to remove duplicate rows after writing.
        """
        self.logger.info(
            "Writing data frame records to the SQLite3 table: %s => %s",
            table,
            sqlite3_file_path,
        )
        with sqlite3.connect(sqlite3_file_path) as c:
            df.to_sql(table, c, if_exists=if_exists, index=index)
            if drop_duplicates:
                self.logger.info("Dropping duplicates in the SQLite3 table: %s", table)
                self.drop_duplicates_in_sqlite3(
                    cursor=c.cursor(),
                    table=table,
                    ids=[str(name) for name in df.index.names],
                )

    def write_df_to_csv(
        self,
        df: pd.DataFrame,
        csv_file_path: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Write DataFrame to CSV file.

        Args:
            df: DataFrame to write.
            csv_file_path: Path to the CSV file.
            **kwargs: Additional parameters for pandas.DataFrame.to_csv().
        """
        self.logger.info("Writing data frame records to CSV file: %s", csv_file_path)
        df.to_csv(csv_file_path, **kwargs)

    def _log_df_info(self, df: pd.DataFrame) -> None:
        """Log DataFrame shape and dtypes.

        Args:
            df: DataFrame to log.
        """
        self.logger.debug("df.shape: %s", df.shape)
        self.logger.debug("df.dtypes: %s", df.dtypes)
        self.logger.debug("df: %s", df)

    def _print_and_write_df(
        self,
        df: pd.DataFrame,
        csv_file_path: str | None = None,
        sqlite3_file_path: str | None = None,
        sqlite3_table: str | None = None,
    ) -> None:
        """Print DataFrame and optionally write to CSV and SQLite.

        Args:
            df: DataFrame to print and export.
            csv_file_path: Path for CSV export (optional).
            sqlite3_file_path: Path for SQLite export (optional).
            sqlite3_table: Table name for SQLite export (optional).
        """
        self._log_df_info(df=df)
        self.print_df(df=df)
        if csv_file_path:
            self.write_df_to_csv(df=df, csv_file_path=csv_file_path)
        if sqlite3_file_path and sqlite3_table:
            self.write_df_to_sqlite3(
                df=df,
                sqlite3_file_path=sqlite3_file_path,
                table=sqlite3_table,
            )

    def print_mt5_info(self) -> None:
        """Print MetaTrader 5 terminal and account information as JSON."""
        self.logger.info("MetaTrader5.__version__: %s", self.mt5.__version__)
        self.logger.info("MetaTrader5.__author__: %s", self.mt5.__author__)
        version_info = self.version_as_dict()
        self.logger.debug("version_info: %s", version_info)
        terminal_info = self.terminal_info_as_dict()
        self.logger.debug("terminal_info: %s", terminal_info)
        account_info = self.account_info_as_dict()
        self.logger.debug("account_info: %s", account_info)
        symbols_total = self.symbols_total()
        self.logger.debug("symbols_total: %s", symbols_total)
        self.print_json(
            data={
                "MetaTrader5": {
                    "version": self.mt5.__version__,
                    "author": self.mt5.__author__,
                },
                "terminal": {
                    "version": version_info,
                    "info": terminal_info,
                },
                "account": account_info,
                "symbols_total": symbols_total,
            },
        )

    def print_symbol_info(self, symbol: str) -> None:
        """Print detailed information about a financial instrument."""
        self.logger.info("symbol: %s", symbol)
        symbol_info = self.symbol_info_as_dict(symbol=symbol)
        self.logger.debug("symbol_info: %s", symbol_info)
        symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
        self.logger.debug("symbol_info_tick: %s", symbol_info_tick)
        self.print_json(
            data={"symbol": symbol, "info": symbol_info, "tick": symbol_info_tick},
        )

    def print_symbols(
        self,
        group: str = "",
        csv_file_path: str | None = None,
        sqlite3_file_path: str | None = None,
    ) -> None:
        """Print available symbols as DataFrame.

        Args:
            group: Symbol group filter (e.g., "*USD*", "Forex*").
            csv_file_path: Path for CSV export (optional).
            sqlite3_file_path: Path for SQLite export (optional).
        """
        self.logger.info("group: %s", group)
        self._print_and_write_df(
            df=self.symbols_get_as_df(group=group),
            csv_file_path=csv_file_path,
            sqlite3_file_path=sqlite3_file_path,
            sqlite3_table="symbols",
        )

    def print_account_info(
        self,
        csv_file_path: str | None = None,
        sqlite3_file_path: str | None = None,
    ) -> None:
        """Print account information as DataFrame.

        Args:
            csv_file_path: Path for CSV export (optional).
            sqlite3_file_path: Path for SQLite export (optional).
        """
        self.logger.info("Fetching account information")
        self._print_and_write_df(
            df=self.account_info_as_df(),
            csv_file_path=csv_file_path,
            sqlite3_file_path=sqlite3_file_path,
            sqlite3_table="account_info",
        )

    def print_terminal_info(
        self,
        csv_file_path: str | None = None,
        sqlite3_file_path: str | None = None,
    ) -> None:
        """Print terminal information as DataFrame.

        Args:
            csv_file_path: Path for CSV export (optional).
            sqlite3_file_path: Path for SQLite export (optional).
        """
        self.logger.info("Fetching terminal information")
        self._print_and_write_df(
            df=self.terminal_info_as_df(),
            csv_file_path=csv_file_path,
            sqlite3_file_path=sqlite3_file_path,
            sqlite3_table="terminal_info",
        )

    def print_rates(
        self,
        symbol: str,
        granularity: str,
        count: int,
        start_pos: int = 0,
        csv_file_path: str | None = None,
        sqlite3_file_path: str | None = None,
    ) -> None:
        """Print OHLC rate data for a symbol as DataFrame.

        Args:
            symbol: Financial instrument symbol.
            granularity: Time granularity (e.g., 'M1', 'H1', 'D1').
            count: Number of bars to fetch.
            start_pos: Starting position (0 = most recent).
            csv_file_path: Path for CSV export (optional).
            sqlite3_file_path: Path for SQLite export (optional).
        """
        self.logger.info(
            "symbol: %s, granularity: %s, count: %s, start_pos: %s",
            symbol,
            granularity,
            count,
            start_pos,
        )
        timeframe = getattr(self.mt5, f"TIMEFRAME_{granularity}")
        self.logger.info("TIMEFRAME_%s: %s", granularity, timeframe)
        self._print_and_write_df(
            df=self.copy_rates_from_pos_as_df(
                symbol=symbol,
                timeframe=timeframe,
                start_pos=start_pos,
                count=count,
            ),
            csv_file_path=csv_file_path,
            sqlite3_file_path=sqlite3_file_path,
            sqlite3_table=f"rate_{symbol}",
        )

    def print_ticks(
        self,
        symbol: str,
        seconds: float,
        date_to: str | None = None,
        csv_file_path: str | None = None,
        sqlite3_file_path: str | None = None,
        count: int = 10000,
    ) -> None:
        """Print tick data for a symbol as DataFrame.

        Args:
            symbol: Financial instrument symbol.
            seconds: Number of seconds of tick data to fetch.
            date_to: End date for data (defaults to latest tick time).
            csv_file_path: Path for CSV export (optional).
            sqlite3_file_path: Path for SQLite export (optional).
            count: Number of ticks to fetch (default is 10000).
        """
        self.logger.info(
            "symbol: %s, seconds: %s, date_to: %s",
            symbol,
            seconds,
            date_to,
        )
        if date_to:
            end_date = pd.to_datetime(date_to)
            start_date = end_date - timedelta(seconds=seconds)
            self.logger.info("start_date: %s, end_date: %s", start_date, end_date)
            df_tick = self.copy_ticks_range_as_df(
                symbol=symbol,
                date_from=start_date,
                date_to=end_date,
                flags=self.mt5.COPY_TICKS_ALL,
            )
        else:
            symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
            last_tick_time = pd.to_datetime(symbol_info_tick["time"], unit="s")
            start_date = last_tick_time - timedelta(seconds=seconds)
            self.logger.info(
                "start_date: %s, last_tick_time: %s",
                start_date,
                last_tick_time,
            )
            df_tick = self.copy_ticks_from_as_df(
                symbol=symbol,
                date_from=start_date,
                count=count,
                flags=self.mt5.COPY_TICKS_ALL,
            )
        self._print_and_write_df(
            df=df_tick,
            csv_file_path=csv_file_path,
            sqlite3_file_path=sqlite3_file_path,
            sqlite3_table=f"tick_{symbol}",
        )

    def print_margins(self, symbol: str) -> None:
        """Print margin requirements for a symbol.

        Args:
            symbol: Financial instrument symbol (e.g., 'EURUSD').
        """
        self.logger.info("symbol: %s", symbol)
        account_info = self.account_info_as_dict()
        self.logger.debug("account_info: %s", account_info)
        symbol_info = self.symbol_info_as_dict(symbol=symbol)
        self.logger.debug("symbol_info: %s", symbol_info)
        symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
        self.logger.debug("symbol_info_tick: %s", symbol_info_tick)
        account_currency = account_info["currency"]
        self.logger.info("account_currency: %s", account_currency)
        volume_min = symbol_info["volume_min"]
        self.logger.info("volume_min: %s", volume_min)
        ask_margin = self.order_calc_margin(
            self.mt5.ORDER_TYPE_BUY, symbol, volume_min, symbol_info_tick["ask"]
        )
        self.logger.info("ask_margin: %s", ask_margin)
        bid_margin = self.order_calc_margin(
            self.mt5.ORDER_TYPE_SELL, symbol, volume_min, symbol_info_tick["bid"]
        )
        self.logger.info("bid_margin: %s", bid_margin)
        self.print_json({
            "symbol": symbol,
            "account_currency": account_currency,
            "volume": volume_min,
            "margin": {"ask": ask_margin, "bid": bid_margin},
        })

    def print_positions(self) -> None:
        """Print open positions for a symbol."""
        self.print_json(data=self.positions_get_as_df().to_dict(orient="records"))

    def print_orders(self) -> None:
        """Print active orders for a symbol."""
        self.print_json(data=self.orders_get_as_df().to_dict(orient="records"))

    def print_history_deals(
        self,
        hours: float,
        date_to: str | None = None,
        group: str | None = None,
        symbol: str | None = None,
    ) -> None:
        """Print trading deals from history as DataFrame.

        Args:
            hours: Number of hours to look back from end date.
            date_to: End date for history search (defaults to now).
            group: Symbol group filter (optional).
            symbol: Symbol filter (optional).
            csv_file_path: Path for CSV export (optional).
            sqlite3_file_path: Path for SQLite export (optional).
        """
        self.logger.info(
            "hours: %s, date_to: %s, group: %s, symbol: %s",
            hours,
            date_to,
            group,
            symbol,
        )
        end_date = pd.to_datetime(date_to) if date_to else datetime.now(UTC)
        start_date = end_date - timedelta(hours=float(hours))
        self.logger.info("start_date: %s, end_date: %s", start_date, end_date)
        self.print_json(
            data=self.history_deals_get_as_df(
                date_from=start_date,
                date_to=end_date,
                group=group,
                symbol=symbol,
            ).to_dict(orient="records"),
        )

    def print_history_orders(
        self,
        hours: float | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        group: str | None = None,
        symbol: str | None = None,
        ticket: int | None = None,
        position: int | None = None,
    ) -> None:
        """Print historical orders as DataFrame.

        Args:
            hours: Number of hours to look back from end date.
            date_from: Start date for history search.
            date_to: End date for history search.
            group: Optional group filter.
            symbol: Optional symbol filter.
            ticket: Get orders by ticket.
            position: Get orders by position.
        """
        self.logger.info(
            "hours: %s, date_from: %s, date_to: %s, group: %s, symbol: %s, "
            "ticket: %s, position: %s",
            hours,
            date_from,
            date_to,
            group,
            symbol,
            ticket,
            position,
        )
        if hours is not None:
            end_date = pd.to_datetime(date_to) if date_to else datetime.now(UTC)
            start_date = end_date - timedelta(hours=hours)
        else:
            start_date = pd.to_datetime(date_from) if date_from else None
            end_date = pd.to_datetime(date_to) if date_to else None
        self.logger.info("start_date: %s, end_date: %s", start_date, end_date)
        self.print_json(
            data=self.history_orders_get_as_df(
                date_from=start_date,
                date_to=end_date,
                group=group,
                symbol=symbol,
                ticket=ticket,
                position=position,
            ).to_dict(orient="records"),
        )
