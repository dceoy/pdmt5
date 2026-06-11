"""pdmt5: Pandas-based data handler for MetaTrader 5."""

from importlib.metadata import version

from .constants import (
    COPY_TICKS_MAP,
    ORDER_TYPE_MAP,
    TIMEFRAME_MAP,
    get_copy_ticks_name,
    get_copy_ticks_value,
    get_order_type_name,
    get_order_type_value,
    get_timeframe_name,
    get_timeframe_value,
    list_copy_ticks_names,
    list_copy_ticks_values,
    list_order_type_names,
    list_order_type_values,
    list_timeframe_names,
    list_timeframe_values,
    parse_copy_ticks,
    parse_order_type,
    parse_timeframe,
)
from .dataframe import Mt5Config, Mt5DataClient
from .mt5 import Mt5Client, Mt5RuntimeError
from .trading import Mt5TradingClient, Mt5TradingError

__version__ = version(__package__) if __package__ else None

__all__ = [
    "COPY_TICKS_MAP",
    "ORDER_TYPE_MAP",
    "TIMEFRAME_MAP",
    "Mt5Client",
    "Mt5Config",
    "Mt5DataClient",
    "Mt5RuntimeError",
    "Mt5TradingClient",
    "Mt5TradingError",
    "get_copy_ticks_name",
    "get_copy_ticks_value",
    "get_order_type_name",
    "get_order_type_value",
    "get_timeframe_name",
    "get_timeframe_value",
    "list_copy_ticks_names",
    "list_copy_ticks_values",
    "list_order_type_names",
    "list_order_type_values",
    "list_timeframe_names",
    "list_timeframe_values",
    "parse_copy_ticks",
    "parse_order_type",
    "parse_timeframe",
]
