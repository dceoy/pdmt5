"""MetaTrader5 data client with pretty printing capabilities."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd

from .manipulator import Mt5DataClient


class Mt5DataPrinter(Mt5DataClient):
    """MetaTrader5 data client with pretty printing capabilities.

    This class extends Mt5DataClient to provide methods for pretty-printing
    DataFrames and other data structures with consistent DataFrame-based operations.
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
        symbol: str | None = None,
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print trading deals from history as DataFrame.

        Retrieves and displays historical trading deals within a specified
        time window, optionally filtered by symbol group.

        Args:
            hours: Number of hours to look back from end date.
            date_to: End date for history search (defaults to now).
            group: Symbol group filter (optional).
            symbol: Symbol filter (optional).
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite export (optional).
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

        df_deals = self.history_deals_get_as_df(
            date_from=start_date,
            date_to=end_date,
            group=group,
            symbol=symbol,
        )

        if df_deals.empty:
            self.logger.info("No deals found")
            print("No deals found")  # noqa: T201
            return

        self.print_df(df=df_deals)
        self.export_df(
            df=df_deals,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table="deals",
        )

    def print_orders(
        self,
        symbol: str | None = None,
        group: str | None = None,
        ticket: int | None = None,
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print current active orders as DataFrame.

        Retrieves and displays all currently active pending orders.

        Args:
            symbol: Optional symbol filter.
            group: Optional group filter.
            ticket: Optional order ticket filter.
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite export (optional).
        """
        self.logger.info("symbol: %s, group: %s, ticket: %s", symbol, group, ticket)

        df_orders = self.orders_get_as_df(
            symbol=symbol,
            group=group,
            ticket=ticket,
        )

        if df_orders.empty:
            self.logger.info("No orders found")
            print("No orders found")  # noqa: T201
            return

        self.print_df(df=df_orders)
        self.export_df(
            df=df_orders,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table="orders",
        )

    def print_positions(
        self,
        symbol: str | None = None,
        group: str | None = None,
        ticket: int | None = None,
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print current open positions as DataFrame.

        Retrieves and displays all currently open trading positions.

        Args:
            symbol: Optional symbol filter.
            group: Optional group filter.
            ticket: Optional position ticket filter.
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite export (optional).
        """
        self.logger.info("symbol: %s, group: %s, ticket: %s", symbol, group, ticket)

        df_positions = self.positions_get_as_df(
            symbol=symbol,
            group=group,
            ticket=ticket,
        )

        if df_positions.empty:
            self.logger.info("No positions found")
            print("No positions found")  # noqa: T201
            return

        self.print_df(df=df_positions)
        self.export_df(
            df=df_positions,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table="positions",
        )

    def print_margins(self, symbol: str) -> None:
        """Print margin requirements for a symbol.

        Calculates and displays minimum margin requirements for buy and sell
        orders of the specified financial instrument.

        Args:
            symbol: Financial instrument symbol (e.g., 'EURUSD').
        """
        self.logger.info("symbol: %s", symbol)
        account_info = self.account_info_as_dict()
        symbol_info = self.symbol_info_as_dict(symbol=symbol)
        symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)

        account_currency = account_info["currency"]
        volume_min = symbol_info["volume_min"]

        self.logger.info("account_currency: %s", account_currency)
        self.logger.info("volume_min: %s", volume_min)
        self.logger.debug("symbol_info_tick: %s", symbol_info_tick)

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

    def print_ticks(
        self,
        symbol: str,
        seconds: float,
        date_to: str | None = None,
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print tick data for a symbol as DataFrame.

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

        if date_to:
            end_date = pd.to_datetime(date_to)
            start_date = end_date - timedelta(seconds=seconds)
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
            df_tick = self.copy_ticks_from_as_df(
                symbol=symbol,
                date_from=start_date,
                count=10000,
                flags=self.mt5.COPY_TICKS_ALL,
            )

        if df_tick.empty:
            self.logger.info("No tick data found")
            print("No tick data found")  # noqa: T201
            return

        self.print_df(df=df_tick)
        self.export_df(
            df=df_tick,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table=f"tick_{symbol}",
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
        """Print OHLC rate data for a symbol as DataFrame.

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

        timeframe = getattr(self.mt5, f"TIMEFRAME_{granularity}")
        self.logger.info("TIMEFRAME_%s: %s", granularity, timeframe)

        df_rate = self.copy_rates_from_pos_as_df(
            symbol=symbol,
            timeframe=timeframe,
            start_pos=start_pos,
            count=count,
        )

        if df_rate.empty:
            self.logger.info("No rate data found")
            print("No rate data found")  # noqa: T201
            return

        self.print_df(df=df_rate)
        self.export_df(
            df=df_rate,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table=f"rate_{symbol}",
        )

    def print_symbol_info(self, symbol: str) -> None:
        """Print detailed information about a financial instrument.

        Retrieves and displays symbol specifications and current tick data
        for the specified financial instrument.

        Args:
            symbol: Financial instrument symbol.
        """
        self.logger.info("symbol: %s", symbol)
        symbol_info = self.symbol_info_as_dict(symbol=symbol)
        symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
        self.logger.debug("symbol_info: %s", symbol_info)
        self.logger.debug("symbol_info_tick: %s", symbol_info_tick)
        self.print_json({
            "symbol": symbol,
            "info": symbol_info,
            "tick": symbol_info_tick,
        })

    def print_mt5_info(self) -> None:
        """Print MetaTrader 5 terminal and account information as JSON.

        Displays MetaTrader 5 version, terminal status and settings,
        trading account information, and available instrument count.
        """
        self.logger.info("MetaTrader5.__version__: %s", self.mt5.__version__)
        self.logger.info("MetaTrader5.__author__: %s", self.mt5.__author__)

        version_info = self.version_as_dict()
        terminal_info = self.terminal_info_as_dict()
        account_info = self.account_info_as_dict()
        symbols_total = self.symbols_total()

        self.logger.debug("version_info: %s", version_info)
        self.logger.debug("terminal_info: %s", terminal_info)
        self.logger.debug("account_info: %s", account_info)

        info_data = {
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
        }

        self.print_json(info_data)

    def print_symbols(
        self,
        group: str = "",
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print available symbols as DataFrame.

        Retrieves and displays all available financial instruments,
        optionally filtered by group.

        Args:
            group: Symbol group filter (e.g., "*USD*", "Forex*").
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite export (optional).
        """
        self.logger.info("group: %s", group)

        df_symbols = self.symbols_get_as_df(group=group)

        if df_symbols.empty:
            self.logger.info("No symbols found")
            print("No symbols found")  # noqa: T201
            return

        self.print_df(df=df_symbols)
        self.export_df(
            df=df_symbols,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table="symbols",
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
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print historical orders as DataFrame.

        Retrieves and displays historical orders with optional filters.

        Args:
            hours: Number of hours to look back from end date.
            date_from: Start date for history search.
            date_to: End date for history search.
            group: Optional group filter.
            symbol: Optional symbol filter.
            ticket: Get orders by ticket.
            position: Get orders by position.
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite export (optional).
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

        df_orders = self.history_orders_get_as_df(
            date_from=start_date,
            date_to=end_date,
            group=group,
            symbol=symbol,
            ticket=ticket,
            position=position,
        )

        if df_orders.empty:
            self.logger.info("No historical orders found")
            print("No historical orders found")  # noqa: T201
            return

        self.print_df(df=df_orders)
        self.export_df(
            df=df_orders,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table="history_orders",
        )

    def print_account_info(
        self,
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print account information as DataFrame.

        Retrieves and displays current account information.

        Args:
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite export (optional).
        """
        self.logger.info("Fetching account information")

        df_account = self.account_info_as_dataframe()

        self.print_df(df=df_account)
        self.export_df(
            df=df_account,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table="account_info",
        )

    def print_terminal_info(
        self,
        csv_path: str | None = None,
        sqlite3_path: str | None = None,
    ) -> None:
        """Print terminal information as DataFrame.

        Retrieves and displays terminal status and settings.

        Args:
            csv_path: Path for CSV export (optional).
            sqlite3_path: Path for SQLite export (optional).
        """
        self.logger.info("Fetching terminal information")

        df_terminal = self.terminal_info_as_dataframe()

        self.print_df(df=df_terminal)
        self.export_df(
            df=df_terminal,
            csv_path=csv_path,
            sqlite3_path=sqlite3_path,
            sqlite3_table="terminal_info",
        )
