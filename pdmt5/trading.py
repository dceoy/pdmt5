"""Trading operations module with advanced MetaTrader5 functionality."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Literal

from pydantic import ConfigDict, Field

from .dataframe import Mt5DataClient
from .mt5 import Mt5RuntimeError

if TYPE_CHECKING:
    import pandas as pd


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
        dry_run: bool | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> dict[str, list[dict[str, Any]]]:
        """Close all open positions for specified symbols.

        Args:
            symbols: Optional symbol or list of symbols to filter positions.
                If None, all symbols will be considered.
            dry_run: Optional flag to enable dry run mode. If None, uses the instance's
                `dry_run` attribute.
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
        self.logger.info("Fetching and closing positions for symbols: %s", symbol_list)
        return {
            s: self._fetch_and_close_position(symbol=s, dry_run=dry_run, **kwargs)
            for s in symbol_list
        }

    def _fetch_and_close_position(
        self,
        symbol: str | None = None,
        dry_run: bool | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> list[dict[str, Any]]:
        """Close all open positions for a specific symbol.

        Args:
            symbol: Optional symbol filter.
            dry_run: Optional flag to enable dry run mode. If None, uses the instance's
                `dry_run` attribute.
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
                    dry_run=dry_run,
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
                `dry_run` attribute.

        Returns:
            Dictionary with operation result.

        Raises:
            Mt5TradingError: If the order operation fails.
        """
        self.logger.debug("request: %s", request)
        is_dry_run = dry_run if dry_run is not None else self.dry_run
        self.logger.debug("is_dry_run: %s", is_dry_run)
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
            self.logger.info("response: %s", response)
            return response
        elif retcode in {
            self.mt5.TRADE_RETCODE_TRADE_DISABLED,
            self.mt5.TRADE_RETCODE_MARKET_CLOSED,
        }:
            self.logger.info("response: %s", response)
            comment = response.get("comment", "Unknown error")
            self.logger.warning("%s() failed and skipped. <= `%s`", order_func, comment)
            return response
        else:
            self.logger.error("response: %s", response)
            comment = response.get("comment", "Unknown error")
            error_message = f"{order_func}() failed and aborted. <= `{comment}`"
            raise Mt5TradingError(error_message)

    def calculate_minimum_order_margins(self, symbol: str) -> dict[str, float]:
        """Calculate minimum order margins for a given symbol.

        Args:
            symbol: Symbol for which to calculate minimum order margins.

        Returns:
            Dictionary with margin information.

        Raises:
            Mt5TradingError: If margin calculation fails.
        """
        symbol_info = self.symbol_info_as_dict(symbol=symbol)
        symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
        min_ask_order_margin = self.order_calc_margin(
            action=self.mt5.ORDER_TYPE_BUY,
            symbol=symbol,
            volume=symbol_info["volume_min"],
            price=symbol_info_tick["ask"],
        )
        min_bid_order_margin = self.order_calc_margin(
            action=self.mt5.ORDER_TYPE_SELL,
            symbol=symbol,
            volume=symbol_info["volume_min"],
            price=symbol_info_tick["bid"],
        )
        min_order_margins = {"ask": min_ask_order_margin, "bid": min_bid_order_margin}
        self.logger.info("Minimum order margins for %s: %s", symbol, min_order_margins)
        if all(min_order_margins.values()):
            return min_order_margins
        else:
            error_message = (
                f"Failed to calculate minimum order margins for symbol: {symbol}."
            )
            raise Mt5TradingError(error_message)

    def calculate_spread_ratio(
        self,
        symbol: str,
    ) -> float:
        """Calculate the spread ratio for a given symbol.

        Args:
            symbol: Symbol for which to calculate the spread ratio.

        Returns:
            Spread ratio as a float.
        """
        symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
        return (
            (symbol_info_tick["ask"] - symbol_info_tick["bid"])
            / (symbol_info_tick["ask"] + symbol_info_tick["bid"])
            * 2
        )

    def fetch_latest_rates_as_df(
        self,
        symbol: str,
        granularity: str = "M1",
        count: int = 1440,
        index_keys: str | None = "time",
    ) -> pd.DataFrame:
        """Fetch rate (OHLC) data as a DataFrame.

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
            timeframe = getattr(self.mt5, f"TIMEFRAME_{granularity.upper()}")
        except AttributeError as e:
            error_message = (
                f"MetaTrader5 does not support the given granularity: {granularity}"
            )
            raise Mt5TradingError(error_message) from e
        else:
            return self.copy_rates_from_pos_as_df(
                symbol=symbol,
                timeframe=timeframe,
                start_pos=0,
                count=count,
                index_keys=index_keys,
            )

    def fetch_latest_ticks_as_df(
        self,
        symbol: str,
        seconds: int = 300,
        index_keys: str | None = "time_msc",
    ) -> pd.DataFrame:
        """Fetch tick data as a DataFrame.

        Args:
            symbol: Symbol to fetch tick data for.
            seconds: Time range in seconds to fetch ticks around the last tick time.
            index_keys: Optional index keys for the DataFrame.

        Returns:
            pd.DataFrame: Tick data with time index.
        """
        last_tick_time = self.symbol_info_tick_as_dict(symbol=symbol)["time"]
        return self.copy_ticks_range_as_df(
            symbol=symbol,
            date_from=(last_tick_time - timedelta(seconds=seconds)),
            date_to=(last_tick_time + timedelta(seconds=seconds)),
            flags=self.mt5.COPY_TICKS_ALL,
            index_keys=index_keys,
        )

    def collect_entry_deals_as_df(
        self,
        symbol: str,
        history_seconds: int = 3600,
        index_keys: str | None = "ticket",
    ) -> pd.DataFrame:
        """Collect entry deals as a DataFrame.

        Args:
            symbol: Symbol to collect entry deals for.
            history_seconds: Time range in seconds to fetch deals around the last tick.
            index_keys: Optional index keys for the DataFrame.

        Returns:
            pd.DataFrame: Entry deals with time index.
        """
        last_tick_time = self.symbol_info_tick_as_dict(symbol=symbol)["time"]
        deals_df = self.history_deals_get_as_df(
            date_from=(last_tick_time - timedelta(seconds=history_seconds)),
            date_to=(last_tick_time + timedelta(seconds=history_seconds)),
            symbol=symbol,
            index_keys=index_keys,
        )
        if deals_df.empty:
            return deals_df
        else:
            return deals_df.pipe(
                lambda d: d[
                    d["entry"]
                    & d["type"].isin({self.mt5.DEAL_TYPE_BUY, self.mt5.DEAL_TYPE_SELL})
                ]
            )

    def fetch_positions_with_metrics_as_df(
        self,
        symbol: str,
    ) -> pd.DataFrame:
        """Fetch open positions as a DataFrame with additional metrics.

        Args:
            symbol: Symbol to fetch positions for.

        Returns:
            pd.DataFrame: DataFrame containing open positions with additional metrics.
        """
        positions_df = self.positions_get_as_df(symbol=symbol)
        if positions_df.empty:
            return positions_df
        else:
            symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
            ask_margin = self.order_calc_margin(
                action=self.mt5.ORDER_TYPE_BUY,
                symbol=symbol,
                volume=1,
                price=symbol_info_tick["ask"],
            )
            bid_margin = self.order_calc_margin(
                action=self.mt5.ORDER_TYPE_SELL,
                symbol=symbol,
                volume=1,
                price=symbol_info_tick["bid"],
            )
            return (
                positions_df.assign(
                    elapsed_seconds=lambda d: (
                        symbol_info_tick["time"] - d["time"]
                    ).dt.total_seconds(),
                    underlier_increase_ratio=lambda d: (
                        d["price_current"] / d["price_open"] - 1
                    ),
                    buy=lambda d: (d["type"] == self.mt5.POSITION_TYPE_BUY),
                    sell=lambda d: (d["type"] == self.mt5.POSITION_TYPE_SELL),
                )
                .assign(
                    buy_i=lambda d: d["buy"].astype(int),
                    sell_i=lambda d: d["sell"].astype(int),
                )
                .assign(
                    sign=lambda d: (d["buy_i"] - d["sell_i"]),
                    margin=lambda d: (
                        (d["buy_i"] * ask_margin + d["sell_i"] * bid_margin)
                        * d["volume"]
                    ),
                )
                .assign(
                    signed_volume=lambda d: (d["volume"] * d["sign"]),
                    signed_margin=lambda d: (d["margin"] * d["sign"]),
                    underlier_profit_ratio=lambda d: (
                        d["underlier_increase_ratio"] * d["sign"]
                    ),
                )
                .drop(columns=["buy_i", "sell_i", "sign", "underlier_increase_ratio"])
            )
