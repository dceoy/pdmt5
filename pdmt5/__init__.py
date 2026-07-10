"""Stable package-root API for low-level MetaTrader 5 access."""

from importlib.metadata import version as _version

from .constants import (
    COPY_TICKS_MAP,
    ORDER_TYPE_MAP,
    TIMEFRAME_MAP,
    parse_copy_ticks,
    parse_order_type,
    parse_timeframe,
)
from .dataframe import Mt5Config, Mt5DataClient
from .mt5 import Mt5Client, Mt5RuntimeError

__version__ = _version(__package__) if __package__ else None

__all__ = [
    "COPY_TICKS_MAP",
    "ORDER_TYPE_MAP",
    "TIMEFRAME_MAP",
    "Mt5Client",
    "Mt5Config",
    "Mt5DataClient",
    "Mt5RuntimeError",
    "__version__",
    "parse_copy_ticks",
    "parse_order_type",
    "parse_timeframe",
]
