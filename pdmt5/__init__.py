"""pdmt5: Pandas-based data handler for MetaTrader 5."""

from importlib.metadata import version

from .dataframe import Mt5Config, Mt5DataClient
from .mt5 import Mt5Client, Mt5RuntimeError
from .report import Mt5ReportClient
from .trading import Mt5TradingClient

__version__ = version(__package__) if __package__ else None

__all__ = [
    "Mt5Client",
    "Mt5Config",
    "Mt5DataClient",
    "Mt5ReportClient",
    "Mt5RuntimeError",
    "Mt5TradingClient",
]
