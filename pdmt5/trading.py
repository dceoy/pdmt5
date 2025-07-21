"""Trading operations module with advanced MetaTrader5 functionality."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import ConfigDict, Field

from .dataframe import Mt5DataClient
from .mt5 import Mt5RuntimeError


class Mt5TradingError(Mt5RuntimeError):
    """MetaTrader5 trading error."""


class Mt5TradingClient(Mt5DataClient):
    """MetaTrader5 trading client with advanced trading operations.

    This class extends Mt5DataClient to provide specialized trading functionality
    including position management, order analysis, and trading performance metrics.
    """

    model_config = ConfigDict(frozen=True)
    order_filling_mode: Literal["IOC", "FOK", "RETURN"] = Field(
        default="IOC",
        description="Order filling mode: 'IOC' (Immediate or Cancel), "
        "'FOK' (Fill or Kill), 'RETURN' (Return if not filled)",
    )
    dry_run: bool = Field(default=False, description="Enable dry run mode for testing.")

    def close_open_positions(
        self,
        symbols: str | list[str] | tuple[str, ...] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> dict[str, list[dict[str, Any]]]:
        """Close all open positions for specified symbols.

        Args:
            symbols: Optional symbol or list of symbols to filter positions.
                If None, all symbols will be considered.
            **kwargs: Additional keyword arguments for request parameters.

        Returns:
            Dictionary with symbols as keys and lists of dictionaries containing
                operation results for each closed position as values.
        """
        if isinstance(symbols, str):
            symbol_list = [symbols]
        elif isinstance(symbols, (list, tuple)):
            symbol_list = symbols
        else:
            symbol_list = self.symbols_get()
        return {
            s: self._fetch_and_close_position(symbol=s, **kwargs) for s in symbol_list
        }

    def _fetch_and_close_position(
        self,
        symbol: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> list[dict[str, Any]]:
        """Close all open positions for a specific symbol.

        Args:
            symbol: Optional symbol filter.
            **kwargs: Additional keyword arguments for request parameters.

        Returns:
            List of dictionaries with operation results for each closed position.
        """
        positions_dict = self.positions_get_as_dicts(symbol=symbol)
        if not positions_dict:
            self.logger.warning("No open positions found for symbol: %s", symbol)
            return []
        else:
            self.logger.info("Closing open positions for symbol: %s", symbol)
            order_filling_type = getattr(
                self.mt5,
                f"ORDER_FILLING_{self.order_filling_mode}",
            )
            return [
                self.send_or_check_order(
                    request={
                        "action": self.mt5.TRADE_ACTION_DEAL,
                        "symbol": p["symbol"],
                        "volume": p["volume"],
                        "type": (
                            self.mt5.ORDER_TYPE_SELL
                            if p["type"] == self.mt5.POSITION_TYPE_BUY
                            else self.mt5.ORDER_TYPE_BUY
                        ),
                        "type_filling": order_filling_type,
                        "type_time": self.mt5.ORDER_TIME_GTC,
                        "position": p["ticket"],
                        **kwargs,
                    },
                )
                for p in positions_dict
            ]

    def send_or_check_order(
        self,
        request: dict[str, Any],
        dry_run: bool | None = None,
    ) -> dict[str, Any]:
        """Send or check an order request.

        Args:
            request: Order request dictionary.
            dry_run: Optional flag to enable dry run mode. If None, uses the instance's

        Returns:
            Dictionary with operation result.

        Raises:
            Mt5TradingError: If the order operation fails.
        """
        self.logger.debug("request: %s", request)
        is_dry_run = dry_run if dry_run is not None else self.dry_run
        if is_dry_run:
            response = self.order_check_as_dict(request=request)
            order_func = "order_check"
        else:
            response = self.order_send_as_dict(request=request)
            order_func = "order_send"
        retcode = response.get("retcode")
        if ((not is_dry_run) and retcode == self.mt5.TRADE_RETCODE_DONE) or (
            is_dry_run and retcode == 0
        ):
            self.logger.info("retcode: %s, response: %s", retcode, response)
            return response
        elif retcode in {
            self.mt5.TRADE_RETCODE_TRADE_DISABLED,
            self.mt5.TRADE_RETCODE_MARKET_CLOSED,
        }:
            self.logger.info("retcode: %s, response: %s", retcode, response)
            comment = response.get("comment", "Unknown error")
            self.logger.warning("%s() failed and skipped. <= `%s`", order_func, comment)
            return response
        else:
            self.logger.error("retcode: %s, response: %s", retcode, response)
            comment = response.get("comment", "Unknown error")
            error_message = f"{order_func}() failed and aborted. <= `{comment}`"
            self.logger.error(error_message)
            raise Mt5TradingError(error_message)
