"""Trading operations module with advanced MetaTrader5 functionality."""

from __future__ import annotations

from datetime import timedelta
from math import floor
from typing import TYPE_CHECKING, Any, Literal

from pydantic import ConfigDict

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

    def close_open_positions(
        self,
        symbols: str | list[str] | tuple[str, ...] | None = None,
        order_filling_mode: Literal["IOC", "FOK", "RETURN"] = "IOC",
        dry_run: bool = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> dict[str, list[dict[str, Any]]]:
        """Close all open positions for specified symbols.

        Args:
            symbols: Optional symbol or list of symbols to filter positions.
                If None, all symbols will be considered.
            order_filling_mode: Order filling mode, either "IOC", "FOK", or "RETURN".
            dry_run: If True, only check the order without sending it.
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
            s: self._fetch_and_close_position(
                symbol=s,
                order_filling_mode=order_filling_mode,
                dry_run=dry_run,
                **kwargs,
            )
            for s in symbol_list
        }

    def _fetch_and_close_position(
        self,
        symbol: str | None = None,
        order_filling_mode: Literal["IOC", "FOK", "RETURN"] = "IOC",
        dry_run: bool = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> list[dict[str, Any]]:
        """Close all open positions for a specific symbol.

        Args:
            symbol: Optional symbol filter.
            order_filling_mode: Order filling mode, either "IOC", "FOK", or "RETURN".
            dry_run: If True, only check the order without sending it.
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
            return [
                self._send_or_check_order(
                    request={
                        "action": self.mt5.TRADE_ACTION_DEAL,
                        "symbol": p["symbol"],
                        "volume": p["volume"],
                        "type": (
                            self.mt5.ORDER_TYPE_SELL
                            if p["type"] == self.mt5.POSITION_TYPE_BUY
                            else self.mt5.ORDER_TYPE_BUY
                        ),
                        "type_filling": getattr(
                            self.mt5,
                            f"ORDER_FILLING_{order_filling_mode}",
                        ),
                        "type_time": self.mt5.ORDER_TIME_GTC,
                        "position": p["ticket"],
                        **kwargs,
                    },
                    dry_run=dry_run,
                )
                for p in positions_dict
            ]

    def _send_or_check_order(
        self,
        request: dict[str, Any],
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Send or check an order request.

        Args:
            request: Order request dictionary.
            dry_run: If True, only check the order without sending it.

        Returns:
            Dictionary with operation result.

        Raises:
            Mt5TradingError: If the order operation fails.
        """
        self.logger.debug("request: %s", request)
        if dry_run:
            response = self.order_check_as_dict(request=request)
            order_func = "order_check"
        else:
            response = self.order_send_as_dict(request=request)
            order_func = "order_send"
        retcode = response.get("retcode")
        if ((not dry_run) and retcode == self.mt5.TRADE_RETCODE_DONE) or (
            dry_run and retcode == 0
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

    def place_market_order(
        self,
        symbol: str,
        volume: float,
        order_side: Literal["BUY", "SELL"],
        order_filling_mode: Literal["IOC", "FOK", "RETURN"] = "IOC",
        order_time_mode: Literal["GTC", "DAY", "SPECIFIED", "SPECIFIED_DAY"] = "GTC",
        dry_run: bool = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> dict[str, Any]:
        """Send or check an order request to place a market order.

        Args:
            symbol: Symbol for the order.
            volume: Volume of the order.
            order_side: Side of the order, either "BUY" or "SELL".
            order_filling_mode: Order filling mode, either "IOC", "FOK", or "RETURN".
            order_time_mode: Order time mode, either "GTC", "DAY", "SPECIFIED",
                or "SPECIFIED_DAY".
            dry_run: If True, only check the order without sending it.
            **kwargs: Additional keyword arguments for request parameters.

        Returns:
            Dictionary with operation result.
        """
        return self._send_or_check_order(
            request={
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": getattr(self.mt5, f"ORDER_TYPE_{order_side.upper()}"),
                "type_filling": getattr(
                    self.mt5, f"ORDER_FILLING_{order_filling_mode.upper()}"
                ),
                "type_time": getattr(self.mt5, f"ORDER_TIME_{order_time_mode.upper()}"),
                **kwargs,
            },
            dry_run=dry_run,
        )

    def update_sltp_for_open_positions(
        self,
        symbol: str,
        stop_loss: float | None = None,
        take_profit: float | None = None,
        tickets: list[int] | None = None,
        dry_run: bool = False,
        **kwargs: Any,  # noqa: ANN401
    ) -> list[dict[str, Any]]:
        """Change Stop Loss and Take Profit for open positions.

        Args:
            symbol: Symbol for the position.
            stop_loss: New Stop Loss price. If None, it will not be changed.
            take_profit: New Take Profit price. If None, it will not be changed.
            tickets: List of position tickets to filter positions. If None, all open
                positions for the symbol will be considered.
            dry_run: If True, only check the order without sending it.
            **kwargs: Additional keyword arguments for request parameters.

        Returns:
            List of dictionaries with operation results for each updated position.
        """
        positions_df = self.positions_get_as_df(symbol=symbol)
        if positions_df.empty:
            self.logger.warning("No open positions found for symbol: %s", symbol)
            return []
        elif tickets:
            filtered_positions_df = positions_df.pipe(
                lambda d: d[d["ticket"].isin(tickets)]
            )
        else:
            filtered_positions_df = positions_df
        if filtered_positions_df.empty:
            self.logger.warning(
                "No open positions found for symbol: %s with specified tickets: %s",
                symbol,
                tickets,
            )
            return []
        else:
            symbol_info = self.symbol_info_as_dict(symbol=symbol)
            sl = round(stop_loss, symbol_info["digits"]) if stop_loss else None
            tp = round(take_profit, symbol_info["digits"]) if take_profit else None
            order_requests = [
                {
                    "action": self.mt5.TRADE_ACTION_SLTP,
                    "symbol": p["symbol"],
                    "position": p["ticket"],
                    "sl": (sl or p["sl"]),
                    "tp": (tp or p["tp"]),
                    **kwargs,
                }
                for _, p in filtered_positions_df.iterrows()
                if sl != p["sl"] or tp != p["tp"]
            ]
            if order_requests:
                return [
                    self._send_or_check_order(request=r, dry_run=dry_run)
                    for r in order_requests
                ]
            else:
                self.logger.info(
                    "No positions to update for symbol: %s with SL: %s and TP: %s",
                    symbol,
                    sl,
                    tp,
                )
                return []

    def calculate_minimum_order_margin(
        self,
        symbol: str,
        order_side: Literal["BUY", "SELL"],
    ) -> dict[str, float]:
        """Calculate the minimum order margins for a given symbol.

        Args:
            symbol: Symbol for which to calculate the minimum order margins.
            order_side: Optional side of the order, either "BUY" or "SELL".

        Returns:
            Dictionary with minimum volume and margin for the specified order side.
        """
        symbol_info = self.symbol_info_as_dict(symbol=symbol)
        symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
        margin = self.order_calc_margin(
            action=getattr(self.mt5, f"ORDER_TYPE_{order_side.upper()}"),
            symbol=symbol,
            volume=symbol_info["volume_min"],
            price=(
                symbol_info_tick["bid"]
                if order_side == "SELL"
                else symbol_info_tick["ask"]
            ),
        )
        if margin:
            return {"volume": symbol_info["volume_min"], "margin": margin}
        else:
            self.logger.warning(
                "No margin available for symbol: %s with order side: %s",
                symbol,
                order_side,
            )
            return {"volume": symbol_info["volume_min"], "margin": 0.0}

    def calculate_volume_by_margin(
        self,
        symbol: str,
        margin: float,
        order_side: Literal["BUY", "SELL"],
    ) -> float:
        """Calculate volume based on margin for a given symbol and order side.

        Args:
            symbol: Symbol for which to calculate the volume.
            margin: Margin amount to use for the calculation.
            order_side: Side of the order, either "BUY" or "SELL".

        Returns:
            Calculated volume as a float.
        """
        min_order_margin_dict = self.calculate_minimum_order_margin(
            symbol=symbol,
            order_side=order_side,
        )
        if min_order_margin_dict["margin"]:
            return (
                floor(margin / min_order_margin_dict["margin"])
                * min_order_margin_dict["volume"]
            )
        else:
            return 0.0

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

    def calculate_new_position_margin_ratio(
        self,
        symbol: str,
        new_position_side: Literal["BUY", "SELL"] | None = None,
        new_position_volume: float = 0,
    ) -> float:
        """Calculate the margin ratio for a new position.

        Args:
            symbol: Symbol for which to calculate the margin ratio.
            new_position_side: Side of the new position, either "BUY" or "SELL".
            new_position_volume: Volume of the new position.

        Returns:
            float: Margin ratio for the new position as a fraction of account equity.
        """
        account_info = self.account_info_as_dict()
        if not account_info["equity"]:
            return 0.0
        else:
            positions_df = self.fetch_positions_with_metrics_as_df(symbol=symbol)
            current_signed_margin = (
                positions_df["signed_margin"].sum() if positions_df.size else 0
            )
            symbol_info_tick = self.symbol_info_tick_as_dict(symbol=symbol)
            if not (new_position_side and new_position_volume):
                new_signed_margin = 0
            elif new_position_side.upper() == "BUY":
                new_signed_margin = self.order_calc_margin(
                    action=self.mt5.ORDER_TYPE_BUY,
                    symbol=symbol,
                    volume=new_position_volume,
                    price=symbol_info_tick["ask"],
                )
            elif new_position_side.upper() == "SELL":
                new_signed_margin = -self.order_calc_margin(
                    action=self.mt5.ORDER_TYPE_SELL,
                    symbol=symbol,
                    volume=new_position_volume,
                    price=symbol_info_tick["bid"],
                )
            else:
                new_signed_margin = 0
            return abs(
                (new_signed_margin + current_signed_margin) / account_info["equity"]
            )
