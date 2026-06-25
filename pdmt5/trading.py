"""Trading operations module for MetaTrader5 order primitives."""

from __future__ import annotations

import logging
from datetime import timedelta
from functools import cached_property
from typing import TYPE_CHECKING, Any, Final, Literal

from pydantic import ConfigDict

from .constants import parse_copy_ticks, parse_order_type, parse_timeframe
from .dataframe import Mt5DataClient
from .mt5 import Mt5RuntimeError

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)

_SUCCESSFUL_TRADE_RETCODE_NAMES: Final[tuple[str, ...]] = (
    "TRADE_RETCODE_PLACED",
    "TRADE_RETCODE_DONE",
    "TRADE_RETCODE_DONE_PARTIAL",
)
_FAILED_TRADE_RETCODE_NAMES: Final[tuple[str, ...]] = (
    "TRADE_RETCODE_REQUOTE",
    "TRADE_RETCODE_REJECT",
    "TRADE_RETCODE_CANCEL",
    "TRADE_RETCODE_ERROR",
    "TRADE_RETCODE_TIMEOUT",
    "TRADE_RETCODE_INVALID",
    "TRADE_RETCODE_INVALID_VOLUME",
    "TRADE_RETCODE_INVALID_PRICE",
    "TRADE_RETCODE_INVALID_STOPS",
    "TRADE_RETCODE_TRADE_DISABLED",
    "TRADE_RETCODE_MARKET_CLOSED",
    "TRADE_RETCODE_NO_MONEY",
    "TRADE_RETCODE_PRICE_CHANGED",
    "TRADE_RETCODE_PRICE_OFF",
    "TRADE_RETCODE_INVALID_EXPIRATION",
    "TRADE_RETCODE_ORDER_CHANGED",
    "TRADE_RETCODE_TOO_MANY_REQUESTS",
    "TRADE_RETCODE_NO_CHANGES",
    "TRADE_RETCODE_SERVER_DISABLES_AT",
    "TRADE_RETCODE_CLIENT_DISABLES_AT",
    "TRADE_RETCODE_LOCKED",
    "TRADE_RETCODE_FROZEN",
    "TRADE_RETCODE_INVALID_FILL",
    "TRADE_RETCODE_CONNECTION",
    "TRADE_RETCODE_ONLY_REAL",
    "TRADE_RETCODE_LIMIT_ORDERS",
    "TRADE_RETCODE_LIMIT_VOLUME",
    "TRADE_RETCODE_INVALID_ORDER",
    "TRADE_RETCODE_POSITION_CLOSED",
    "TRADE_RETCODE_INVALID_CLOSE_VOLUME",
    "TRADE_RETCODE_CLOSE_ORDER_EXIST",
    "TRADE_RETCODE_LIMIT_POSITIONS",
    "TRADE_RETCODE_REJECT_CANCEL",
    "TRADE_RETCODE_LONG_ONLY",
    "TRADE_RETCODE_SHORT_ONLY",
    "TRADE_RETCODE_CLOSE_ONLY",
    "TRADE_RETCODE_FIFO_CLOSE",
    "TRADE_RETCODE_HEDGE_PROHIBITED",
)


class Mt5TradingError(Mt5RuntimeError):
    """MetaTrader5 trading error."""


class Mt5TradingClient(Mt5DataClient):
    """MetaTrader5 trading client providing direct order primitives.

    This class extends ``Mt5DataClient`` with thin wrappers around
    ``order_check`` / ``order_send`` and convenience helpers for common
    single-call patterns.

    Higher-level operational orchestration (margin-budget sizing, broker
    constraint pre-checks, position-metric computation, batch workflows) belongs
    in ``mt5cli``, the canonical downstream operational SDK built on ``pdmt5``.
    """

    model_config = ConfigDict(frozen=True)

    @cached_property
    def mt5_successful_trade_retcodes(self) -> set[int]:
        """Set of successful trade return codes.

        Maps ``TRADE_RETCODE_PLACED``, ``TRADE_RETCODE_DONE``, and
        ``TRADE_RETCODE_DONE_PARTIAL`` from the MetaTrader5 module into an
        integer set for retcode validation.

        Returns:
            Set of successful trade return codes.
        """
        return {
            int(getattr(self.mt5, name)) for name in _SUCCESSFUL_TRADE_RETCODE_NAMES
        }

    @cached_property
    def mt5_failed_trade_retcodes(self) -> set[int]:
        """Set of failed trade return codes.

        Maps all ``TRADE_RETCODE_*`` failure constants from the MetaTrader5
        module into an integer set for retcode validation.

        Returns:
            Set of failed trade return codes.
        """
        return {int(getattr(self.mt5, name)) for name in _FAILED_TRADE_RETCODE_NAMES}

    def _send_or_check_order(
        self,
        request: dict[str, Any],
        raise_on_error: bool = False,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Send or check an order request.

        Routes to ``order_check`` (dry run) or ``order_send`` (live) and
        validates the returned retcode.

        Args:
            request: Order request dictionary.
            raise_on_error: If True, raise an error on operation failure.
            dry_run: If True, only check the order without sending it.

        Returns:
            Dictionary with operation result.

        Raises:
            Mt5TradingError: If the order operation fails.
        """
        logger.debug("request: %s", request)
        if dry_run:
            response = self.order_check_as_dict(request=request)
            order_func = "order_check"
        else:
            response = self.order_send_as_dict(request=request)
            order_func = "order_send"
        retcode = response.get("retcode")
        if (dry_run and retcode == 0) or (
            not dry_run and retcode in self.mt5_successful_trade_retcodes
        ):
            logger.info("response: %s", response)
            return response
        if raise_on_error:
            logger.error("response: %s", response)
            comment = response.get("comment")
            error_message = f"{order_func}() failed and aborted. <= `{comment}`"
            raise Mt5TradingError(error_message)
        logger.warning("response: %s", response)
        comment = response.get("comment")
        logger.warning("%s() failed and skipped. <= `%s`", order_func, comment)
        return response

    def place_market_order(
        self,
        symbol: str,
        volume: float,
        order_side: Literal["BUY", "SELL"],
        order_filling_mode: Literal["IOC", "FOK", "RETURN"] = "IOC",
        order_time_mode: Literal["GTC", "DAY", "SPECIFIED", "SPECIFIED_DAY"] = "GTC",
        raise_on_error: bool = False,
        dry_run: bool = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> dict[str, Any]:
        """Send or check a market order request.

        Builds a ``TRADE_ACTION_DEAL`` request from the provided parameters and
        delegates to ``_send_or_check_order``.

        Args:
            symbol: Symbol for the order.
            volume: Volume of the order.
            order_side: Side of the order, either "BUY" or "SELL".
            order_filling_mode: Order filling mode, either "IOC", "FOK", or "RETURN".
            order_time_mode: Order time mode, either "GTC", "DAY", "SPECIFIED",
                or "SPECIFIED_DAY".
            raise_on_error: If True, raise an error on operation failure.
            dry_run: If True, only check the order without sending it.
            **kwargs: Additional keyword arguments for request parameters.

        Returns:
            Dictionary with operation result.
        """
        logger.info("Placing market order: %s %s %s", order_side, volume, symbol)
        return self._send_or_check_order(
            request={
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": parse_order_type(order_side),
                "type_filling": getattr(
                    self.mt5, f"ORDER_FILLING_{order_filling_mode.upper()}"
                ),
                "type_time": getattr(self.mt5, f"ORDER_TIME_{order_time_mode.upper()}"),
                **kwargs,
            },
            raise_on_error=raise_on_error,
            dry_run=dry_run,
        )

    def calculate_minimum_order_margin(
        self,
        symbol: str,
        order_side: Literal["BUY", "SELL"],
    ) -> dict[str, float]:
        """Calculate the minimum order margin for a given symbol and side.

        Combines ``symbol_info`` and ``order_calc_margin`` to return the margin
        required for the broker's minimum allowable volume.

        Args:
            symbol: Symbol for which to calculate the minimum order margin.
            order_side: Side of the order, either "BUY" or "SELL".

        Returns:
            Dictionary with minimum volume and margin for the specified order side.
        """
        symbol_info = self.symbol_info_as_dict(symbol=symbol)
        symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
        margin = self.order_calc_margin(
            action=parse_order_type(order_side),
            symbol=symbol,
            volume=symbol_info["volume_min"],
            price=(
                symbol_info_tick["bid"]
                if order_side == "SELL"
                else symbol_info_tick["ask"]
            ),
        )
        result = {"volume": symbol_info["volume_min"], "margin": margin}
        if margin:
            logger.info(
                "Calculated minimum %s order margin for %s: %s",
                order_side,
                symbol,
                result,
            )
        else:
            logger.warning(
                "Calculated minimum order margin to %s %s: %s",
                order_side,
                symbol,
                result,
            )
        return result

    def fetch_latest_rates_as_df(
        self,
        symbol: str,
        granularity: str = "M1",
        count: int = 1440,
        index_keys: str | None = "time",
    ) -> pd.DataFrame:
        """Fetch the most recent OHLC bars as a DataFrame.

        Resolves the ``granularity`` string (e.g. ``"M1"``, ``"H1"``) via
        ``parse_timeframe`` and calls ``copy_rates_from_pos_as_df`` from
        position 0.

        Args:
            symbol: Symbol to fetch data for.
            granularity: Time granularity as a timeframe suffix (e.g., "M1", "H1").
            count: Number of bars to fetch.
            index_keys: Optional index keys for the DataFrame.

        Returns:
            pd.DataFrame: OHLC data with time index.

        Raises:
            Mt5TradingError: If the granularity is not supported by MetaTrader5.
        """
        try:
            timeframe = parse_timeframe(granularity)
        except ValueError as e:
            error_message = (
                f"MetaTrader5 does not support the given granularity: {granularity}"
            )
            raise Mt5TradingError(error_message) from e
        result = self.copy_rates_from_pos_as_df(
            symbol=symbol,
            timeframe=timeframe,
            start_pos=0,
            count=count,
            index_keys=index_keys,
        )
        logger.info(
            "Fetched latest %s rates for %s: %d rows",
            granularity,
            symbol,
            result.shape[0],
        )
        return result

    def fetch_latest_ticks_as_df(
        self,
        symbol: str,
        seconds: int = 300,
        index_keys: str | None = "time_msc",
    ) -> pd.DataFrame:
        """Fetch recent tick data as a DataFrame.

        Derives a date range centred on the last tick time and calls
        ``copy_ticks_range_as_df``.

        Args:
            symbol: Symbol to fetch tick data for.
            seconds: Time range in seconds to fetch ticks around the last tick time.
            index_keys: Optional index keys for the DataFrame.

        Returns:
            pd.DataFrame: Tick data with time index.
        """
        last_tick_time = self.symbol_info_tick_as_dict(symbol=symbol)["time"]
        result = self.copy_ticks_range_as_df(
            symbol=symbol,
            date_from=(last_tick_time - timedelta(seconds=seconds)),
            date_to=(last_tick_time + timedelta(seconds=seconds)),
            flags=parse_copy_ticks("ALL"),
            index_keys=index_keys,
        )
        logger.info(
            "Fetched latest ticks for %s: %d rows",
            symbol,
            result.shape[0],
        )
        return result
