"""MetaTrader5 manipulator with pandas DataFrame conversion."""

from __future__ import annotations

import importlib
import json
import logging
import os
import sqlite3
import time
from datetime import UTC, datetime, timedelta
from types import ModuleType  # noqa: TC003
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from types import TracebackType

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class Mt5RuntimeError(RuntimeError):
    """MetaTrader5 specific error."""


class Mt5Config(BaseModel):
    """Configuration for MetaTrader5 connection."""

    model_config = ConfigDict(frozen=True)
    path: str | None = Field(
        default=None, description="Path to MetaTrader5 terminal EXE file"
    )
    login: int | None = Field(default=None, description="Trading account login")
    password: str | None = Field(default=None, description="Trading account password")
    server: str | None = Field(default=None, description="Trading server name")
    timeout: int | None = Field(
        default=None, description="Connection timeout in milliseconds"
    )
    portable: bool | None = Field(default=None, description="Use portable mode")


class Mt5DataClient(BaseModel):
    """MetaTrader5 data client with pandas DataFrame conversion.

    This class provides a pandas-friendly interface to MetaTrader5 functions,
    converting native MetaTrader5 data structures to pandas DataFrames with pydantic
    validation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    config: Mt5Config = Field(
        default_factory=lambda: Mt5Config(),  # pyright: ignore[reportCallIssue] # noqa: PLW0108
        description="MetaTrader5 connection configuration",
    )
    retry_count: int = Field(
        default=3,
        description="Number of retry attempts for connection initialization",
    )
    mt5: ModuleType = Field(
        default_factory=lambda: importlib.import_module("MetaTrader5"),
        description="MetaTrader5 module instance",
    )
    logger: logging.Logger = Field(
        default_factory=lambda: logging.getLogger(__name__),
        description="Logger instance for MetaTrader5 operations",
    )
    _is_initialized: bool = False

    def __enter__(self) -> Self:
        """Context manager entry.

        Returns:
            Mt5DataClient: The data client instance.
        """
        self.initialize()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.shutdown()

    def last_error(self) -> tuple[int, str]:
        """Get last MetaTrader5 error code and description.

        Returns:
            Tuple of (error_code, error_description).
        """
        return self.mt5.last_error()

    def _handle_error(self, operation: str, context: str | None = None) -> None:
        """Handle MetaTrader5 errors by raising appropriate exception.

        Args:
            operation: Name of the operation that failed.
            context: Additional context about the operation.

        Raises:
            Mt5RuntimeError: With error details from MetaTrader5.
        """
        error_code, error_description = self.last_error()
        error_message = f"{operation} failed: {error_code} - {error_description}" + (
            f" (context: {context})" if context else ""
        )
        self.logger.error(error_message)
        raise Mt5RuntimeError(error_message)

    def initialize(self) -> bool:
        """Initialize MetaTrader5 connection.

        Returns:
            True if successful, False otherwise.
        """
        if self._is_initialized:
            return True

        initialize_args = [self.config.path] if self.config.path else []
        initialize_kwargs = {
            k: getattr(self.config, k)
            for k in ["login", "password", "server", "timeout", "portable"]
            if getattr(self.config, k) is not None
        }
        result: bool = False
        for i in range(1 + max(0, self.retry_count)):
            if result:
                break
            elif i == 0:
                self.logger.info("Initialize MetaTrader5")
            elif i > 0:
                self.logger.warning("Retry MetaTrader5.initialize()")
                time.sleep(i)
            result: bool = self.mt5.initialize(*initialize_args, **initialize_kwargs)
        if not result:
            self._handle_error(
                operation="initialize",
                context=", ".join(
                    initialize_args
                    + [
                        (f"{k}={v}" if k != "password" else f"{k}=***")
                        for k, v in initialize_kwargs.items()
                    ]
                ),
            )
        self._is_initialized = True
        self.logger.info("MetaTrader5 connection initialized successfully")
        return True

    def shutdown(self) -> None:
        """Shutdown MetaTrader5 connection."""
        if self._is_initialized:
            self.mt5.shutdown()
            self._is_initialized = False
            self.logger.info("MetaTrader5 connection shutdown")

    def _ensure_initialized(self) -> None:
        """Ensure MetaTrader5 is initialized."""
        if not self._is_initialized:
            self.initialize()

    def account_info(self) -> pd.DataFrame:
        """Get account information as DataFrame.

        Returns:
            DataFrame with account information.
        """
        self._ensure_initialized()

        account_info = self.mt5.account_info()
        if account_info is None:
            self._handle_error("account_info")

        account_dict = account_info._asdict()
        return pd.DataFrame([account_dict])

    def terminal_info(self) -> pd.DataFrame:
        """Get terminal information as DataFrame.

        Returns:
            DataFrame with terminal information.
        """
        self._ensure_initialized()

        terminal_info = self.mt5.terminal_info()
        if terminal_info is None:
            self._handle_error("terminal_info")

        terminal_dict = terminal_info._asdict()
        return pd.DataFrame([terminal_dict])

    def copy_rates_from(
        self,
        symbol: str,
        timeframe: int,
        date_from: datetime,
        count: int,
    ) -> pd.DataFrame:
        """Get rates from specified date as DataFrame.

        Args:
            symbol: Symbol name.
            timeframe: Timeframe constant.
            date_from: Start date.
            count: Number of rates to retrieve.

        Returns:
            DataFrame with OHLCV data indexed by time.
        """
        self._ensure_initialized()

        self._validate_positive_count(count)

        rates = self.mt5.copy_rates_from(symbol, timeframe, date_from, count)
        if rates is None or len(rates) == 0:
            context = (
                f"symbol={symbol}, timeframe={timeframe}, "
                f"from={date_from}, count={count}"
            )
            self._handle_error("copy_rates_from", context)

        rates_df = pd.DataFrame(rates)
        rates_df = self._convert_standard_time_columns(rates_df)
        return rates_df.set_index("time")

    def copy_rates_from_pos(
        self,
        symbol: str,
        timeframe: int,
        start_pos: int,
        count: int,
    ) -> pd.DataFrame:
        """Get rates from specified position as DataFrame.

        Args:
            symbol: Symbol name.
            timeframe: Timeframe constant.
            start_pos: Start position.
            count: Number of rates to retrieve.

        Returns:
            DataFrame with OHLCV data indexed by time.
        """
        self._ensure_initialized()

        self._validate_positive_count(count)
        self._validate_non_negative_position(start_pos)

        rates = self.mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
        if rates is None or len(rates) == 0:
            context = (
                f"symbol={symbol}, timeframe={timeframe}, "
                f"pos={start_pos}, count={count}"
            )
            self._handle_error("copy_rates_from_pos", context)

        rates_df = pd.DataFrame(rates)
        rates_df = self._convert_standard_time_columns(rates_df)
        return rates_df.set_index("time")

    def copy_rates_range(
        self,
        symbol: str,
        timeframe: int,
        date_from: datetime,
        date_to: datetime,
    ) -> pd.DataFrame:
        """Get rates for specified date range as DataFrame.

        Args:
            symbol: Symbol name.
            timeframe: Timeframe constant.
            date_from: Start date.
            date_to: End date.

        Returns:
            DataFrame with OHLCV data indexed by time.
        """
        self._ensure_initialized()

        self._validate_date_range(date_from, date_to)

        rates = self.mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
        if rates is None or len(rates) == 0:
            context = (
                f"symbol={symbol}, timeframe={timeframe}, "
                f"from={date_from}, to={date_to}"
            )
            self._handle_error("copy_rates_range", context)

        rates_df = pd.DataFrame(rates)
        rates_df = self._convert_standard_time_columns(rates_df)
        return rates_df.set_index("time")

    def copy_ticks_from(
        self,
        symbol: str,
        date_from: datetime,
        count: int,
        flags: int,
    ) -> pd.DataFrame:
        """Get ticks from specified date as DataFrame.

        Args:
            symbol: Symbol name.
            date_from: Start date.
            count: Number of ticks to retrieve.
            flags: Tick flags (use constants from MetaTrader5).

        Returns:
            DataFrame with tick data indexed by time.
        """
        self._ensure_initialized()

        self._validate_positive_count(count)

        ticks = self.mt5.copy_ticks_from(symbol, date_from, count, flags)
        if ticks is None or len(ticks) == 0:
            context = f"symbol={symbol}, from={date_from}, count={count}, flags={flags}"
            self._handle_error("copy_ticks_from", context)

        ticks_df = pd.DataFrame(ticks)
        ticks_df = self._convert_standard_time_columns(ticks_df)
        return ticks_df.set_index("time")

    def copy_ticks_range(
        self,
        symbol: str,
        date_from: datetime,
        date_to: datetime,
        flags: int,
    ) -> pd.DataFrame:
        """Get ticks for specified date range as DataFrame.

        Args:
            symbol: Symbol name.
            date_from: Start date.
            date_to: End date.
            flags: Tick flags (use constants from MetaTrader5).

        Returns:
            DataFrame with tick data indexed by time.
        """
        self._ensure_initialized()

        self._validate_date_range(date_from, date_to)

        ticks = self.mt5.copy_ticks_range(symbol, date_from, date_to, flags)
        if ticks is None or len(ticks) == 0:
            context = f"symbol={symbol}, from={date_from}, to={date_to}, flags={flags}"
            self._handle_error("copy_ticks_range", context)

        ticks_df = pd.DataFrame(ticks)
        ticks_df = self._convert_standard_time_columns(ticks_df)
        return ticks_df.set_index("time")

    def symbols_get(self, group: str = "") -> pd.DataFrame:
        """Get symbols as DataFrame.

        Args:
            group: Symbol group filter (e.g., "*USD*", "Forex*").

        Returns:
            DataFrame with symbol information.
        """
        self._ensure_initialized()

        symbols = self.mt5.symbols_get(group)
        if symbols is None or len(symbols) == 0:
            context = f"group={group}" if group else "all symbols"
            self._handle_error("symbols_get", context)

        symbol_dicts = [symbol._asdict() for symbol in symbols]
        return pd.DataFrame(symbol_dicts)

    def symbol_info(self, symbol: str) -> pd.DataFrame:
        """Get symbol information as DataFrame.

        Args:
            symbol: Symbol name.

        Returns:
            DataFrame with symbol information.
        """
        self._ensure_initialized()

        symbol_info = self.mt5.symbol_info(symbol)
        if symbol_info is None:
            self._handle_error("symbol_info", f"symbol={symbol}")

        symbol_dict = symbol_info._asdict()
        return pd.DataFrame([symbol_dict])

    def symbol_info_tick(self, symbol: str) -> pd.DataFrame:
        """Get symbol tick information as DataFrame.

        Args:
            symbol: Symbol name.

        Returns:
            DataFrame with current tick information.
        """
        self._ensure_initialized()

        tick_info = self.mt5.symbol_info_tick(symbol)
        if tick_info is None:
            self._handle_error("symbol_info_tick", f"symbol={symbol}")

        tick_dict = tick_info._asdict()
        # Convert time fields manually for dictionary
        tick_dict["time"] = pd.to_datetime(tick_dict["time"], unit="s")
        if "time_msc" in tick_dict:
            tick_dict["time_msc"] = pd.to_datetime(tick_dict["time_msc"], unit="ms")
        return pd.DataFrame([tick_dict])

    def orders_get(self, symbol: str | None = None, group: str = "") -> pd.DataFrame:
        """Get active orders as DataFrame.

        Args:
            symbol: Optional symbol filter.
            group: Optional group filter.

        Returns:
            DataFrame with order information or empty DataFrame if no orders.
        """
        self._ensure_initialized()

        if symbol:
            orders = self.mt5.orders_get(symbol=symbol)
        else:
            orders = self.mt5.orders_get(group=group)

        if orders is None or len(orders) == 0:
            return pd.DataFrame()

        order_dicts = [order._asdict() for order in orders]
        orders_df = pd.DataFrame(order_dicts)

        time_columns = ["time_setup", "time_expiration", "time_done"]
        orders_df = self._convert_time_columns(orders_df, time_columns)

        return orders_df

    def positions_get(self, symbol: str | None = None, group: str = "") -> pd.DataFrame:
        """Get open positions as DataFrame.

        Args:
            symbol: Optional symbol filter.
            group: Optional group filter.

        Returns:
            DataFrame with position information or empty DataFrame if no positions.
        """
        self._ensure_initialized()

        if symbol:
            positions = self.mt5.positions_get(symbol=symbol)
        else:
            positions = self.mt5.positions_get(group=group)

        if positions is None or len(positions) == 0:
            return pd.DataFrame()

        position_dicts = [position._asdict() for position in positions]
        positions_df = pd.DataFrame(position_dicts)

        # Convert time columns with different units
        time_columns_s = ["time", "time_update"]
        time_columns_ms = ["time_msc", "time_update_msc"]
        positions_df = self._convert_time_columns(positions_df, time_columns_s, "s")
        positions_df = self._convert_time_columns(positions_df, time_columns_ms, "ms")

        return positions_df

    def history_orders_get(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        symbol: str | None = None,
        group: str = "",
        ticket: int | None = None,
        position: int | None = None,
    ) -> pd.DataFrame:
        """Get historical orders as DataFrame.

        Args:
            date_from: Start date (required if not using ticket/position).
            date_to: End date (required if not using ticket/position).
            symbol: Optional symbol filter.
            group: Optional group filter.
            ticket: Get orders by ticket.
            position: Get orders by position.

        Returns:
            DataFrame with historical order information.

        Raises:
            ValueError: If date_from and date_to are not provided when not using
                ticket/position, or if date_from is not before date_to.
        """
        self._ensure_initialized()

        if ticket is not None:
            orders = self.mt5.history_orders_get(ticket=ticket)
        elif position is not None:
            orders = self.mt5.history_orders_get(position=position)
        else:
            if date_from is None or date_to is None:
                error_message = (
                    "date_from and date_to are required when not filtering "
                    "by ticket/position"
                )
                raise ValueError(error_message)
            self._validate_date_range(date_from, date_to)

            if symbol:
                orders = self.mt5.history_orders_get(date_from, date_to, symbol=symbol)
            else:
                orders = self.mt5.history_orders_get(date_from, date_to, group=group)

        if orders is None or len(orders) == 0:
            return pd.DataFrame()

        order_dicts = [order._asdict() for order in orders]
        history_orders_df = pd.DataFrame(order_dicts)

        time_columns = ["time_setup", "time_expiration", "time_done"]
        history_orders_df = self._convert_time_columns(history_orders_df, time_columns)

        return history_orders_df

    def history_deals_get(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        symbol: str | None = None,
        group: str = "",
        ticket: int | None = None,
        position: int | None = None,
    ) -> pd.DataFrame:
        """Get historical deals as DataFrame.

        Args:
            date_from: Start date (required if not using ticket/position).
            date_to: End date (required if not using ticket/position).
            symbol: Optional symbol filter.
            group: Optional group filter.
            ticket: Get deals by order ticket.
            position: Get deals by position ticket.

        Returns:
            DataFrame with historical deal information.

        Raises:
            ValueError: If date_from and date_to are not provided when not using
                ticket/position, or if date_from is not before date_to.
        """
        self._ensure_initialized()

        if ticket is not None:
            deals = self.mt5.history_deals_get(ticket=ticket)
        elif position is not None:
            deals = self.mt5.history_deals_get(position=position)
        else:
            if date_from is None or date_to is None:
                error_message = (
                    "date_from and date_to are required when not filtering "
                    "by ticket/position"
                )
                raise ValueError(error_message)
            self._validate_date_range(date_from, date_to)

            if symbol:
                deals = self.mt5.history_deals_get(date_from, date_to, symbol=symbol)
            else:
                deals = self.mt5.history_deals_get(date_from, date_to, group=group)

        if deals is None or len(deals) == 0:
            return pd.DataFrame()

        deal_dicts = [deal._asdict() for deal in deals]
        history_deals_df = pd.DataFrame(deal_dicts)

        history_deals_df = self._convert_standard_time_columns(history_deals_df)

        return history_deals_df

    def login(
        self,
        login: int,
        password: str,
        server: str,
        timeout: int | None = None,
    ) -> bool:
        """Connect to trading account.

        Args:
            login: Trading account number.
            password: Trading account password.
            server: Trade server address.
            timeout: Connection timeout in milliseconds.

        Returns:
            True if successful, False otherwise.
        """
        self._ensure_initialized()

        kwargs = {
            "login": login,
            "password": password,
            "server": server,
        }
        if timeout is not None:
            kwargs["timeout"] = timeout

        result = self.mt5.login(**kwargs)
        if not result:
            self._handle_error("login", f"account={login}, server={server}")

        return result

    def order_check(self, request: dict[str, Any]) -> pd.DataFrame:
        """Check funds sufficiency for a trade operation.

        Args:
            request: Trade request dictionary with required fields:
                - action: Trade operation type
                - symbol: Symbol name
                - volume: Requested volume
                - type: Order type
                - price: Price
                Optional fields include sl, tp, deviation, magic, comment, etc.

        Returns:
            DataFrame with check results including retcode, balance, equity,
            margin, etc.
        """
        self._ensure_initialized()

        result = self.mt5.order_check(request)
        if result is None:
            self._handle_error("order_check", f"request={request}")

        result_dict = result._asdict()
        return pd.DataFrame([result_dict])

    def order_send(self, request: dict[str, Any]) -> pd.DataFrame:
        """Send trade request to server.

        Args:
            request: Trade request dictionary with required fields:
                - action: Trade operation type
                - symbol: Symbol name
                - volume: Requested volume
                - type: Order type
                - price: Price (for pending orders)
                Optional fields include sl, tp, deviation, magic, comment, etc.

        Returns:
            DataFrame with trade result including retcode, deal, order, volume,
            price, etc.
        """
        self._ensure_initialized()

        result = self.mt5.order_send(request)
        if result is None:
            self._handle_error("order_send", f"request={request}")

        result_dict = result._asdict()
        return pd.DataFrame([result_dict])

    def orders_total(self) -> int:
        """Get total number of active orders.

        Returns:
            Number of active orders.
        """
        self._ensure_initialized()

        total = self.mt5.orders_total()
        if total is None:
            self._handle_error("orders_total")

        return total

    def positions_total(self) -> int:
        """Get total number of open positions.

        Returns:
            Number of open positions.
        """
        self._ensure_initialized()

        total = self.mt5.positions_total()
        if total is None:
            self._handle_error("positions_total")

        return total

    def history_orders_total(
        self,
        date_from: datetime,
        date_to: datetime,
    ) -> int:
        """Get total number of orders in history for the specified period.

        Args:
            date_from: Period start date.
            date_to: Period end date.

        Returns:
            Number of historical orders.
        """
        self._ensure_initialized()

        self._validate_date_range(date_from, date_to)

        total = self.mt5.history_orders_total(date_from, date_to)
        if total is None:
            self._handle_error(
                "history_orders_total", f"from={date_from}, to={date_to}"
            )

        return total

    def history_deals_total(
        self,
        date_from: datetime,
        date_to: datetime,
    ) -> int:
        """Get total number of deals in history for the specified period.

        Args:
            date_from: Period start date.
            date_to: Period end date.

        Returns:
            Number of historical deals.
        """
        self._ensure_initialized()

        self._validate_date_range(date_from, date_to)

        total = self.mt5.history_deals_total(date_from, date_to)
        if total is None:
            self._handle_error("history_deals_total", f"from={date_from}, to={date_to}")

        return total

    def order_calc_margin(
        self,
        action: int,
        symbol: str,
        volume: float,
        price: float,
    ) -> float:
        """Calculate margin required for a specified order.

        Args:
            action: Order type (ORDER_TYPE_BUY or ORDER_TYPE_SELL).
            symbol: Symbol name.
            volume: Volume in lots.
            price: Open price.

        Returns:
            Required margin amount.
        """
        self._ensure_initialized()

        self._validate_positive_value(volume, "volume")
        self._validate_positive_value(price, "price")

        margin = self.mt5.order_calc_margin(action, symbol, volume, price)
        if margin is None:
            context = (
                f"action={action}, symbol={symbol}, volume={volume}, price={price}"
            )
            self._handle_error("order_calc_margin", context)

        return margin

    def order_calc_profit(
        self,
        action: int,
        symbol: str,
        volume: float,
        price_open: float,
        price_close: float,
    ) -> float:
        """Calculate profit for a specified order.

        Args:
            action: Order type (ORDER_TYPE_BUY or ORDER_TYPE_SELL).
            symbol: Symbol name.
            volume: Volume in lots.
            price_open: Open price.
            price_close: Close price.

        Returns:
            Calculated profit.
        """
        self._ensure_initialized()

        self._validate_positive_value(volume, "volume")
        self._validate_positive_value(price_open, "price_open")
        self._validate_positive_value(price_close, "price_close")

        profit = self.mt5.order_calc_profit(
            action,
            symbol,
            volume,
            price_open,
            price_close,
        )
        if profit is None:
            context = (
                f"action={action}, symbol={symbol}, volume={volume}, "
                f"open={price_open}, close={price_close}"
            )
            self._handle_error("order_calc_profit", context)

        return profit

    def version(self) -> tuple[int, int, str]:
        """Get MetaTrader5 version information.

        Returns:
            Tuple of (version, build, release_date).
        """
        self._ensure_initialized()

        version_info = self.mt5.version()
        if version_info is None:
            self._handle_error("version")

        return version_info

    def symbols_total(self) -> int:
        """Get total number of symbols.

        Returns:
            Total number of symbols.
        """
        self._ensure_initialized()

        total = self.mt5.symbols_total()
        if total is None:
            self._handle_error("symbols_total")

        return total

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        """Select symbol in Market Watch.

        Args:
            symbol: Symbol name.
            enable: True to enable, False to disable.

        Returns:
            True if successful, False otherwise.
        """
        self._ensure_initialized()

        result = self.mt5.symbol_select(symbol, enable)
        if result is None:
            self._handle_error("symbol_select")

        return result

    def market_book_add(self, symbol: str) -> bool:
        """Subscribe to market depth for symbol.

        Args:
            symbol: Symbol name.

        Returns:
            True if successful, False otherwise.
        """
        self._ensure_initialized()

        result = self.mt5.market_book_add(symbol)
        if result is None:
            self._handle_error("market_book_add")

        return result

    def market_book_release(self, symbol: str) -> bool:
        """Unsubscribe from market depth for symbol.

        Args:
            symbol: Symbol name.

        Returns:
            True if successful, False otherwise.
        """
        self._ensure_initialized()

        result = self.mt5.market_book_release(symbol)
        if result is None:
            self._handle_error("market_book_release")

        return result

    def market_book_get(self, symbol: str) -> pd.DataFrame:
        """Get market depth information as DataFrame.

        Args:
            symbol: Symbol name.

        Returns:
            DataFrame with market depth information.
        """
        self._ensure_initialized()

        book = self.mt5.market_book_get(symbol)
        if book is None or len(book) == 0:
            self._handle_error("market_book_get")

        book_dicts = [item._asdict() for item in book]
        return pd.DataFrame(book_dicts)

    @staticmethod
    def _validate_positive_count(count: int) -> None:
        """Validate that count is positive.

        Args:
            count: Count value to validate.

        Raises:
            ValueError: If count is not positive.
        """
        if count <= 0:
            error_message = f"Invalid count: {count}. Count must be positive."
            raise ValueError(error_message)

    @staticmethod
    def _validate_date_range(date_from: datetime, date_to: datetime) -> None:
        """Validate that date_from is before date_to.

        Args:
            date_from: Start date.
            date_to: End date.

        Raises:
            ValueError: If date_from is not before date_to.
        """
        if date_from >= date_to:
            error_message = (
                f"Invalid date range: from={date_from} must be before to={date_to}"
            )
            raise ValueError(error_message)

    @staticmethod
    def _validate_positive_value(value: float, name: str) -> None:
        """Validate that a value is positive.

        Args:
            value: Value to validate.
            name: Name of the value for error message.

        Raises:
            ValueError: If value is not positive.
        """
        if value <= 0:
            # For price_open and price_close, use just "Price" in the message
            if name.startswith("price_"):
                display_name = "Price"
            else:
                display_name = name.replace("_", " ").capitalize()
            error_message = f"Invalid {name}: {value}. {display_name} must be positive."
            raise ValueError(error_message)

    @staticmethod
    def _validate_non_negative_position(position: int) -> None:
        """Validate that position is non-negative.

        Args:
            position: Position value to validate.

        Raises:
            ValueError: If position is negative.
        """
        if position < 0:
            error_message = (
                f"Invalid start_pos: {position}. Position must be non-negative."
            )
            raise ValueError(error_message)

    @staticmethod
    def _convert_time_columns(
        df: pd.DataFrame, time_columns: list[str], unit: str = "s"
    ) -> pd.DataFrame:
        """Convert time columns to datetime format.

        Args:
            df: DataFrame to convert.
            time_columns: List of column names to convert.
            unit: Time unit ('s' for seconds, 'ms' for milliseconds).

        Returns:
            DataFrame with converted time columns.
        """
        for col in time_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], unit=unit)
        return df

    @staticmethod
    def _convert_standard_time_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Convert standard time columns (time, time_msc) to datetime.

        Args:
            df: DataFrame to convert.

        Returns:
            DataFrame with converted time columns.
        """
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], unit="s")
        if "time_msc" in df.columns:
            df["time_msc"] = pd.to_datetime(df["time_msc"], unit="ms")
        return df


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
            {"table": table, "ids_str": ", ".join(ids)},
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
