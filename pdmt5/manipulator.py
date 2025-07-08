"""Core MetaTrader5 wrapper with pandas DataFrame conversion."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from datetime import datetime
    from types import ModuleType, TracebackType

logger = logging.getLogger(__name__)


class Mt5Error(RuntimeError):
    """MetaTrader5 specific error."""


class Mt5Config(BaseModel):
    """Configuration for MetaTrader5 connection."""

    model_config = ConfigDict(frozen=True)
    login: int | None = Field(None, description="Trading account login")
    password: str | None = Field(None, description="Trading account password")
    server: str | None = Field(None, description="Trading server name")
    timeout: int = Field(60000, description="Connection timeout in milliseconds")
    portable: bool = Field(default=False, description="Use portable mode")


class Mt5DataClient(BaseModel):
    """MetaTrader5 data client with pandas DataFrame conversion.

    This class provides a pandas-friendly interface to MetaTrader5 functions,
    converting native MetaTrader5 data structures to pandas DataFrames with pydantic
    validation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    mt5: ModuleType = Field(description="MetaTrader5 module instance")
    config: Mt5Config = Field(
        default_factory=lambda: Mt5Config(),  # pyright: ignore[reportCallIssue]  # noqa: PLW0108
        description="MetaTrader5 connection configuration",
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

    def initialize(self, path: str | None = None) -> bool:
        """Initialize MetaTrader5 connection.

        Args:
            path: Optional path to Mt5 terminal.

        Returns:
            True if successful, False otherwise.

        Raises:
            Mt5Error: If initialization fails.
        """
        if self._is_initialized:
            return True
        else:
            success = self.mt5.initialize(
                path=path,
                login=self.config.login,
                password=self.config.password,
                server=self.config.server,
                timeout=self.config.timeout,
                portable=self.config.portable,
            )

            if not success:
                error_code, error_description = self.mt5.last_error()
                msg = (
                    "MetaTrader5 initialization failed: "
                    f"{error_code} - {error_description}"
                )
                raise Mt5Error(msg)
            else:
                self._is_initialized = True
                logger.info("MetaTrader5 connection initialized successfully")
                return True

    def shutdown(self) -> None:
        """Shutdown MetaTrader5 connection."""
        if self._is_initialized:
            self.mt5.shutdown()
            self._is_initialized = False
            logger.info("MetaTrader5 connection shutdown")

    def _ensure_initialized(self) -> None:
        """Ensure MetaTrader5 is initialized."""
        if not self._is_initialized:
            self.initialize()

    def _handle_error(self, operation: str) -> None:
        """Handle MetaTrader5 errors by raising appropriate exception.

        Args:
            operation: Name of the operation that failed.

        Raises:
            Mt5Error: With error details from MetaTrader5.
        """
        error_code, error_description = self.mt5.last_error()
        msg = f"{operation} failed: {error_code} - {error_description}"
        raise Mt5Error(msg)

    def account_info(self) -> pd.DataFrame:
        """Get account information as DataFrame.

        Returns:
            DataFrame with account information.
        """
        self._ensure_initialized()

        account_info = self.mt5.account_info()
        if account_info is None:
            self._handle_error("account_info")

        # Convert named tuple to dict then to DataFrame
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

        # Convert named tuple to dict then to DataFrame
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
            DataFrame with OHLCV data.
        """
        self._ensure_initialized()

        rates = self.mt5.copy_rates_from(symbol, timeframe, date_from, count)
        if rates is None or len(rates) == 0:
            self._handle_error("copy_rates_from")

        # Convert to DataFrame and set proper datetime index
        rates_df = pd.DataFrame(rates)
        rates_df["time"] = pd.to_datetime(rates_df["time"], unit="s")
        rates_df = rates_df.set_index("time")

        return rates_df

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
            DataFrame with OHLCV data.
        """
        self._ensure_initialized()

        rates = self.mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
        if rates is None or len(rates) == 0:
            self._handle_error("copy_rates_from_pos")

        # Convert to DataFrame and set proper datetime index
        rates_df = pd.DataFrame(rates)
        rates_df["time"] = pd.to_datetime(rates_df["time"], unit="s")
        rates_df = rates_df.set_index("time")

        return rates_df

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
            DataFrame with OHLCV data.
        """
        self._ensure_initialized()

        rates = self.mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
        if rates is None or len(rates) == 0:
            self._handle_error("copy_rates_range")

        # Convert to DataFrame and set proper datetime index
        rates_df = pd.DataFrame(rates)
        rates_df["time"] = pd.to_datetime(rates_df["time"], unit="s")
        rates_df = rates_df.set_index("time")

        return rates_df

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
            flags: Tick flags.

        Returns:
            DataFrame with tick data.
        """
        self._ensure_initialized()

        ticks = self.mt5.copy_ticks_from(symbol, date_from, count, flags)
        if ticks is None or len(ticks) == 0:
            self._handle_error("copy_ticks_from")

        # Convert to DataFrame and set proper datetime index
        ticks_df = pd.DataFrame(ticks)
        ticks_df["time"] = pd.to_datetime(ticks_df["time"], unit="s")
        ticks_df = ticks_df.set_index("time")

        return ticks_df

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
            flags: Tick flags.

        Returns:
            DataFrame with tick data.
        """
        self._ensure_initialized()

        ticks = self.mt5.copy_ticks_range(symbol, date_from, date_to, flags)
        if ticks is None or len(ticks) == 0:
            self._handle_error("copy_ticks_range")

        # Convert to DataFrame and set proper datetime index
        ticks_df = pd.DataFrame(ticks)
        ticks_df["time"] = pd.to_datetime(ticks_df["time"], unit="s")
        ticks_df = ticks_df.set_index("time")

        return ticks_df

    def symbols_get(self, group: str = "") -> pd.DataFrame:
        """Get symbols as DataFrame.

        Args:
            group: Symbol group filter.

        Returns:
            DataFrame with symbol information.
        """
        self._ensure_initialized()

        symbols = self.mt5.symbols_get(group)
        if symbols is None or len(symbols) == 0:
            self._handle_error("symbols_get")

        # Convert array of named tuples to DataFrame
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
            self._handle_error("symbol_info")

        # Convert named tuple to dict then to DataFrame
        symbol_dict = symbol_info._asdict()
        return pd.DataFrame([symbol_dict])

    def symbol_info_tick(self, symbol: str) -> pd.DataFrame:
        """Get symbol tick information as DataFrame.

        Args:
            symbol: Symbol name.

        Returns:
            DataFrame with tick information.
        """
        self._ensure_initialized()

        tick_info = self.mt5.symbol_info_tick(symbol)
        if tick_info is None:
            self._handle_error("symbol_info_tick")

        # Convert named tuple to dict then to DataFrame
        tick_dict = tick_info._asdict()
        # Convert time to datetime
        tick_dict["time"] = pd.to_datetime(tick_dict["time"], unit="s")
        return pd.DataFrame([tick_dict])

    def orders_get(self, symbol: str | None = None, group: str = "") -> pd.DataFrame:
        """Get orders as DataFrame.

        Args:
            symbol: Optional symbol filter.
            group: Optional group filter.

        Returns:
            DataFrame with order information.
        """
        self._ensure_initialized()

        if symbol:
            orders = self.mt5.orders_get(symbol=symbol)
        else:
            orders = self.mt5.orders_get(group=group)

        if orders is None or len(orders) == 0:
            # Return empty DataFrame with expected columns
            return pd.DataFrame()

        # Convert array of named tuples to DataFrame
        order_dicts = [order._asdict() for order in orders]
        orders_df = pd.DataFrame(order_dicts)

        # Convert time columns to datetime
        time_columns = ["time_setup", "time_expiration", "time_done"]
        for col in time_columns:
            if col in orders_df.columns:
                orders_df[col] = pd.to_datetime(orders_df[col], unit="s")

        return orders_df

    def positions_get(self, symbol: str | None = None, group: str = "") -> pd.DataFrame:
        """Get positions as DataFrame.

        Args:
            symbol: Optional symbol filter.
            group: Optional group filter.

        Returns:
            DataFrame with position information.
        """
        self._ensure_initialized()

        if symbol:
            positions = self.mt5.positions_get(symbol=symbol)
        else:
            positions = self.mt5.positions_get(group=group)

        if positions is None or len(positions) == 0:
            # Return empty DataFrame with expected columns
            return pd.DataFrame()

        # Convert array of named tuples to DataFrame
        position_dicts = [position._asdict() for position in positions]
        positions_df = pd.DataFrame(position_dicts)

        # Convert time columns to datetime
        time_columns = ["time", "time_update", "time_msc", "time_update_msc"]
        for col in time_columns:
            if col in positions_df.columns:
                if col.endswith("_msc"):
                    positions_df[col] = pd.to_datetime(positions_df[col], unit="ms")
                else:
                    positions_df[col] = pd.to_datetime(positions_df[col], unit="s")

        return positions_df

    def history_orders_get(
        self,
        date_from: datetime,
        date_to: datetime,
        symbol: str | None = None,
        group: str = "",
    ) -> pd.DataFrame:
        """Get historical orders as DataFrame.

        Args:
            date_from: Start date.
            date_to: End date.
            symbol: Optional symbol filter.
            group: Optional group filter.

        Returns:
            DataFrame with historical order information.
        """
        self._ensure_initialized()

        if symbol:
            orders = self.mt5.history_orders_get(date_from, date_to, symbol=symbol)
        else:
            orders = self.mt5.history_orders_get(date_from, date_to, group=group)

        if orders is None or len(orders) == 0:
            # Return empty DataFrame with expected columns
            return pd.DataFrame()

        # Convert array of named tuples to DataFrame
        order_dicts = [order._asdict() for order in orders]
        history_orders_df = pd.DataFrame(order_dicts)

        # Convert time columns to datetime
        time_columns = ["time_setup", "time_expiration", "time_done"]
        for col in time_columns:
            if col in history_orders_df.columns:
                history_orders_df[col] = pd.to_datetime(
                    history_orders_df[col],
                    unit="s",
                )

        return history_orders_df

    def history_deals_get(
        self,
        date_from: datetime,
        date_to: datetime,
        symbol: str | None = None,
        group: str = "",
    ) -> pd.DataFrame:
        """Get historical deals as DataFrame.

        Args:
            date_from: Start date.
            date_to: End date.
            symbol: Optional symbol filter.
            group: Optional group filter.

        Returns:
            DataFrame with historical deal information.
        """
        self._ensure_initialized()

        if symbol:
            deals = self.mt5.history_deals_get(date_from, date_to, symbol=symbol)
        else:
            deals = self.mt5.history_deals_get(date_from, date_to, group=group)

        if deals is None or len(deals) == 0:
            # Return empty DataFrame with expected columns
            return pd.DataFrame()

        # Convert array of named tuples to DataFrame
        deal_dicts = [deal._asdict() for deal in deals]
        history_deals_df = pd.DataFrame(deal_dicts)

        # Convert time columns to datetime
        time_columns = ["time", "time_msc"]
        for col in time_columns:
            if col in history_deals_df.columns:
                if col.endswith("_msc"):
                    history_deals_df[col] = pd.to_datetime(
                        history_deals_df[col],
                        unit="ms",
                    )
                else:
                    history_deals_df[col] = pd.to_datetime(
                        history_deals_df[col],
                        unit="s",
                    )

        return history_deals_df
