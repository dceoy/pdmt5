"""MetaTrader5 client wrapper class."""

# ruff: noqa: ANN401

from __future__ import annotations

import importlib
import logging
from types import ModuleType  # noqa: TC003
from typing import TYPE_CHECKING, Any, Self

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from datetime import datetime
    from types import TracebackType


class Mt5RuntimeError(RuntimeError):
    """MetaTrader5 specific error."""


class Mt5Client(BaseModel):
    """MetaTrader5 client class.

    This class provides a wrapper interface to all MetaTrader5 functions,
    delegating calls to the underlying MetaTrader5 module while providing
    error handling and logging capabilities.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
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
            Mt5Client: The client instance.
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

    def _ensure_initialized(self) -> None:
        """Ensure MetaTrader5 is initialized.

        Raises:
            Mt5RuntimeError: If MetaTrader5 is not initialized.
        """
        if not self._is_initialized:
            error_message = "MetaTrader5 not initialized. Call initialize() first."
            raise Mt5RuntimeError(error_message)

    def initialize(
        self,
        path: str | None = None,
        login: int | None = None,
        password: str | None = None,
        server: str | None = None,
        timeout: int | None = None,
        portable: bool | None = None,
    ) -> bool:
        """Establish a connection with the MetaTrader 5 terminal.

        Args:
            path: Path to the MetaTrader 5 terminal EXE file.
            login: Trading account number.
            password: Trading account password.
            server: Trade server address.
            timeout: Connection timeout in milliseconds.
            portable: Use portable mode.

        Returns:
            True if successful, False otherwise.
        """
        if self._is_initialized:
            return True

        args = [path] if path else []
        kwargs = {}
        if login is not None:
            kwargs["login"] = login
        if password is not None:
            kwargs["password"] = password
        if server is not None:
            kwargs["server"] = server
        if timeout is not None:
            kwargs["timeout"] = timeout
        if portable is not None:
            kwargs["portable"] = portable

        result = self.mt5.initialize(*args, **kwargs)
        if result:
            self._is_initialized = True
            self.logger.info("MetaTrader5 connection initialized successfully")
        else:
            self._handle_error("initialize")
        return result

    def login(
        self,
        login: int,
        password: str,
        server: str,
        timeout: int | None = None,
    ) -> bool:
        """Connect to a trading account using specified parameters.

        Args:
            login: Trading account number.
            password: Trading account password.
            server: Trade server address.
            timeout: Connection timeout in milliseconds.

        Returns:
            True if successful, False otherwise.
        """
        self._ensure_initialized()
        kwargs = {"login": login, "password": password, "server": server}
        if timeout is not None:
            kwargs["timeout"] = timeout
        result = self.mt5.login(**kwargs)
        if not result:
            self._handle_error(
                "login",
                f"login={login}, server={server}, timeout={timeout}",
            )
        return result

    def shutdown(self) -> None:
        """Close the previously established connection to the MetaTrader 5 terminal."""
        if self._is_initialized:
            self.mt5.shutdown()
            self._is_initialized = False
            self.logger.info("MetaTrader5 connection shutdown")

    def version(self) -> tuple[int, int, str]:
        """Return the MetaTrader 5 terminal version.

        Returns:
            Tuple of (terminal_version, build, release_date).
        """
        self._ensure_initialized()
        result = self.mt5.version()
        if result is None:
            self._handle_error("version")
        return result

    def last_error(self) -> tuple[int, str]:
        """Return data on the last error.

        Returns:
            Tuple of (error_code, error_description).
        """
        return self.mt5.last_error()

    def account_info(self) -> Any:
        """Get info on the current trading account.

        Returns:
            AccountInfo structure or None.
        """
        self._ensure_initialized()
        result = self.mt5.account_info()
        if result is None:
            self._handle_error("account_info")
        return result

    def terminal_info(self) -> Any:
        """Get the connected MetaTrader 5 client terminal status and settings.

        Returns:
            TerminalInfo structure or None.
        """
        self._ensure_initialized()
        result = self.mt5.terminal_info()
        if result is None:
            self._handle_error("terminal_info")
        return result

    def symbols_total(self) -> int:
        """Get the number of all financial instruments in the terminal.

        Returns:
            Total number of symbols.
        """
        self._ensure_initialized()
        result = self.mt5.symbols_total()
        if result is None:
            self._handle_error("symbols_total")
        return result

    def symbols_get(self, group: str = "") -> tuple[Any, ...] | None:
        """Get all financial instruments from the terminal.

        Args:
            group: Symbol group filter.

        Returns:
            Tuple of symbol info structures or None.
        """
        self._ensure_initialized()
        result = self.mt5.symbols_get(group) if group else self.mt5.symbols_get()
        if result is None:
            self._handle_error("symbols_get", f"group={group}")
        return result

    def symbol_info(self, symbol: str) -> Any:
        """Get data on the specified financial instrument.

        Args:
            symbol: Symbol name.

        Returns:
            Symbol info structure or None.
        """
        self._ensure_initialized()
        result = self.mt5.symbol_info(symbol)
        if result is None:
            self._handle_error("symbol_info", f"symbol={symbol}")
        return result

    def symbol_info_tick(self, symbol: str) -> Any:
        """Get the last tick for the specified financial instrument.

        Args:
            symbol: Symbol name.

        Returns:
            Tick info structure or None.
        """
        self._ensure_initialized()
        result = self.mt5.symbol_info_tick(symbol)
        if result is None:
            self._handle_error("symbol_info_tick", f"symbol={symbol}")
        return result

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        """Select a symbol in the MarketWatch window or remove a symbol from the window.

        Args:
            symbol: Symbol name.
            enable: True to show, False to hide.

        Returns:
            True if successful, False otherwise.
        """
        self._ensure_initialized()
        result = self.mt5.symbol_select(symbol, enable)
        if result is None:
            self._handle_error("symbol_select", f"symbol={symbol}, enable={enable}")
        return result

    def market_book_add(self, symbol: str) -> bool:
        """Subscribe the terminal to the Market Depth change events for a specified symbol.

        Args:
            symbol: Symbol name.

        Returns:
            True if successful, False otherwise.
        """  # noqa: E501
        self._ensure_initialized()
        result = self.mt5.market_book_add(symbol)
        if not result:
            self._handle_error("market_book_add", f"symbol={symbol}")
        return result

    def market_book_release(self, symbol: str) -> bool:
        """Cancels subscription of the terminal to the Market Depth change events for a specified symbol.

        Args:
            symbol: Symbol name.

        Returns:
            True if successful, False otherwise.
        """  # noqa: E501
        self._ensure_initialized()
        result = self.mt5.market_book_release(symbol)
        if not result:
            self._handle_error("market_book_release", f"symbol={symbol}")
        return result

    def market_book_get(self, symbol: str) -> tuple[Any, ...] | None:
        """Return a tuple from BookInfo featuring Market Depth entries for the specified symbol.

        Args:
            symbol: Symbol name.

        Returns:
            Tuple of BookInfo structures or None.
        """  # noqa: E501
        self._ensure_initialized()
        result = self.mt5.market_book_get(symbol)
        if result is None:
            self._handle_error("market_book_get", f"symbol={symbol}")
        return result

    def copy_rates_from(
        self,
        symbol: str,
        timeframe: int,
        date_from: datetime | int,
        count: int,
    ) -> Any:
        """Get bars from the terminal starting from the specified date.

        Args:
            symbol: Symbol name.
            timeframe: Timeframe constant.
            date_from: Start date or timestamp.
            count: Number of bars to retrieve.

        Returns:
            Array of rates or None.
        """
        self._ensure_initialized()
        result = self.mt5.copy_rates_from(symbol, timeframe, date_from, count)
        if result is None:
            self._handle_error(
                "copy_rates_from",
                f"symbol={symbol}, timeframe={timeframe}, "
                f"date_from={date_from}, count={count}",
            )
        return result

    def copy_rates_from_pos(
        self,
        symbol: str,
        timeframe: int,
        start_pos: int,
        count: int,
    ) -> Any:
        """Get bars from the terminal starting from the specified index.

        Args:
            symbol: Symbol name.
            timeframe: Timeframe constant.
            start_pos: Starting position.
            count: Number of bars to retrieve.

        Returns:
            Array of rates or None.
        """
        self._ensure_initialized()
        result = self.mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
        if result is None:
            self._handle_error(
                "copy_rates_from_pos",
                f"symbol={symbol}, timeframe={timeframe}, "
                f"start_pos={start_pos}, count={count}",
            )
        return result

    def copy_rates_range(
        self,
        symbol: str,
        timeframe: int,
        date_from: datetime | int,
        date_to: datetime | int,
    ) -> Any:
        """Get bars in the specified date range from the terminal.

        Args:
            symbol: Symbol name.
            timeframe: Timeframe constant.
            date_from: Start date or timestamp.
            date_to: End date or timestamp.

        Returns:
            Array of rates or None.
        """
        self._ensure_initialized()
        result = self.mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
        if result is None:
            self._handle_error(
                "copy_rates_range",
                f"symbol={symbol}, timeframe={timeframe}, "
                f"date_from={date_from}, date_to={date_to}",
            )
        return result

    def copy_ticks_from(
        self,
        symbol: str,
        date_from: datetime | int,
        count: int,
        flags: int,
    ) -> Any:
        """Get ticks from the terminal starting from the specified date.

        Args:
            symbol: Symbol name.
            date_from: Start date or timestamp.
            count: Number of ticks to retrieve.
            flags: Tick flags.

        Returns:
            Array of ticks or None.
        """
        self._ensure_initialized()
        result = self.mt5.copy_ticks_from(symbol, date_from, count, flags)
        if result is None:
            self._handle_error(
                "copy_ticks_from",
                f"symbol={symbol}, date_from={date_from}, count={count}, flags={flags}",
            )
        return result

    def copy_ticks_range(
        self,
        symbol: str,
        date_from: datetime | int,
        date_to: datetime | int,
        flags: int,
    ) -> Any:
        """Get ticks for the specified date range from the terminal.

        Args:
            symbol: Symbol name.
            date_from: Start date or timestamp.
            date_to: End date or timestamp.
            flags: Tick flags.

        Returns:
            Array of ticks or None.
        """
        self._ensure_initialized()
        result = self.mt5.copy_ticks_range(symbol, date_from, date_to, flags)
        if result is None:
            self._handle_error(
                "copy_ticks_range",
                f"symbol={symbol}, date_from={date_from}, "
                f"date_to={date_to}, flags={flags}",
            )
        return result

    def orders_total(self) -> int:
        """Get the number of active orders.

        Returns:
            Number of active orders.
        """
        self._ensure_initialized()
        result = self.mt5.orders_total()
        if result is None:
            self._handle_error("orders_total")
        return result

    def orders_get(
        self,
        symbol: str | None = None,
        group: str | None = None,
        ticket: int | None = None,
    ) -> tuple[Any, ...] | None:
        """Get active orders with the ability to filter by symbol or ticket.

        Args:
            symbol: Symbol name filter.
            group: Group filter.
            ticket: Order ticket filter.

        Returns:
            Tuple of order info structures or None.
        """
        self._ensure_initialized()
        kwargs = {}
        if symbol is not None:
            kwargs["symbol"] = symbol
        if group is not None:
            kwargs["group"] = group
        if ticket is not None:
            kwargs["ticket"] = ticket
        result = self.mt5.orders_get(**(kwargs or {}))
        return result

    def order_calc_margin(
        self,
        action: int,
        symbol: str,
        volume: float,
        price: float,
    ) -> float | None:
        """Return margin in the account currency to perform a specified trading operation.

        Args:
            action: Order type (ORDER_TYPE_BUY or ORDER_TYPE_SELL).
            symbol: Symbol name.
            volume: Volume in lots.
            price: Open price.

        Returns:
            Required margin amount or None.
        """  # noqa: E501
        self._ensure_initialized()
        result = self.mt5.order_calc_margin(action, symbol, volume, price)
        if result is None:
            self._handle_error(
                "order_calc_margin",
                f"action={action}, symbol={symbol}, volume={volume}, price={price}",
            )
        return result

    def order_calc_profit(
        self,
        action: int,
        symbol: str,
        volume: float,
        price_open: float,
        price_close: float,
    ) -> float | None:
        """Return profit in the account currency for a specified trading operation.

        Args:
            action: Order type (ORDER_TYPE_BUY or ORDER_TYPE_SELL).
            symbol: Symbol name.
            volume: Volume in lots.
            price_open: Open price.
            price_close: Close price.

        Returns:
            Calculated profit or None.
        """
        self._ensure_initialized()
        result = self.mt5.order_calc_profit(
            action, symbol, volume, price_open, price_close
        )
        if result is None:
            self._handle_error(
                "order_calc_profit",
                f"action={action}, symbol={symbol}, volume={volume}, "
                f"price_open={price_open}, price_close={price_close}",
            )
        return result

    def order_check(self, request: dict[str, Any]) -> Any:
        """Check funds sufficiency for performing a required trading operation.

        Args:
            request: Trade request dictionary.

        Returns:
            OrderCheckResult structure or None.
        """
        self._ensure_initialized()
        result = self.mt5.order_check(request)
        if result is None:
            self._handle_error("order_check", f"request={request}")
        return result

    def order_send(self, request: dict[str, Any]) -> Any:
        """Send a request to perform a trading operation from the terminal to the trade server.

        Args:
            request: Trade request dictionary.

        Returns:
            OrderSendResult structure or None.
        """  # noqa: E501
        self._ensure_initialized()
        result = self.mt5.order_send(request)
        if result is None:
            self._handle_error("order_send", f"request={request}")
        return result

    def positions_total(self) -> int:
        """Get the number of open positions.

        Returns:
            Number of open positions.
        """
        self._ensure_initialized()
        result = self.mt5.positions_total()
        if result is None:
            self._handle_error("positions_total")
        return result

    def positions_get(
        self,
        symbol: str | None = None,
        group: str | None = None,
        ticket: int | None = None,
    ) -> tuple[Any, ...] | None:
        """Get open positions with the ability to filter by symbol or ticket.

        Args:
            symbol: Symbol name filter.
            group: Group filter.
            ticket: Position ticket filter.

        Returns:
            Tuple of position info structures or None.
        """
        self._ensure_initialized()
        kwargs = {}
        if symbol is not None:
            kwargs["symbol"] = symbol
        if group is not None:
            kwargs["group"] = group
        if ticket is not None:
            kwargs["ticket"] = ticket
        result = self.mt5.positions_get(**(kwargs or {}))
        return result

    def history_orders_total(
        self,
        date_from: datetime | int,
        date_to: datetime | int,
    ) -> int:
        """Get the number of orders in trading history within the specified interval.

        Args:
            date_from: Start date or timestamp.
            date_to: End date or timestamp.

        Returns:
            Number of historical orders.
        """
        self._ensure_initialized()
        result = self.mt5.history_orders_total(date_from, date_to)
        if result is None:
            self._handle_error(
                "history_orders_total", f"date_from={date_from}, date_to={date_to}"
            )
        return result

    def history_orders_get(
        self,
        date_from: datetime | int | None = None,
        date_to: datetime | int | None = None,
        group: str | None = None,
        ticket: int | None = None,
        position: int | None = None,
    ) -> tuple[Any, ...] | None:
        """Get orders from trading history with the ability to filter by ticket or position.

        Args:
            date_from: Start date or timestamp.
            date_to: End date or timestamp.
            group: Group filter.
            ticket: Order ticket filter.
            position: Position ticket filter.

        Returns:
            Tuple of historical order info structures or None.

        Raises:
            ValueError: If date_from and date_to are not provided when not filtering
                by ticket/position.
        """  # noqa: E501
        self._ensure_initialized()
        if ticket is not None:
            result = self.mt5.history_orders_get(ticket=ticket)
        elif position is not None:
            result = self.mt5.history_orders_get(position=position)
        else:
            if date_from is None or date_to is None:
                error_message = (
                    "date_from and date_to are required when not filtering "
                    "by ticket/position"
                )
                raise ValueError(error_message)
            kwargs = {}
            if group is not None:
                kwargs["group"] = group
            result = self.mt5.history_orders_get(date_from, date_to, **(kwargs or {}))
        return result

    def history_deals_total(
        self,
        date_from: datetime | int,
        date_to: datetime | int,
    ) -> int:
        """Get the number of deals in trading history within the specified interval.

        Args:
            date_from: Start date or timestamp.
            date_to: End date or timestamp.

        Returns:
            Number of historical deals.
        """
        self._ensure_initialized()
        result = self.mt5.history_deals_total(date_from, date_to)
        if result is None:
            self._handle_error(
                "history_deals_total", f"date_from={date_from}, date_to={date_to}"
            )
        return result

    def history_deals_get(
        self,
        date_from: datetime | int | None = None,
        date_to: datetime | int | None = None,
        group: str | None = None,
        ticket: int | None = None,
        position: int | None = None,
    ) -> tuple[Any, ...] | None:
        """Get deals from trading history within the specified interval with the ability to filter by ticket or position.

        Args:
            date_from: Start date or timestamp.
            date_to: End date or timestamp.
            group: Group filter.
            ticket: Order ticket filter.
            position: Position ticket filter.

        Returns:
            Tuple of historical deal info structures or None.

        Raises:
            ValueError: If date_from and date_to are not provided when not filtering
                by ticket/position.
        """  # noqa: E501
        self._ensure_initialized()
        if ticket is not None:
            result = self.mt5.history_deals_get(ticket=ticket)
        elif position is not None:
            result = self.mt5.history_deals_get(position=position)
        else:
            if date_from is None or date_to is None:
                error_message = (
                    "date_from and date_to are required when not filtering "
                    "by ticket/position"
                )
                raise ValueError(error_message)
            kwargs = {}
            if group is not None:
                kwargs["group"] = group
            result = self.mt5.history_deals_get(date_from, date_to, **(kwargs or {}))
        return result
