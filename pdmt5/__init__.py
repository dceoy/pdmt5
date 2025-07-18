"""pdmt5: Pandas-based data handler for MetaTrader 5."""

from importlib.metadata import version

from .dataframe import Mt5Config, Mt5DataClient
from .etl import Mt5DataPrinter
from .mt5 import Mt5Client, Mt5RuntimeError

__version__ = version(__package__) if __package__ else None

__all__ = [
    "Mt5Client",
    "Mt5Config",
    "Mt5DataClient",
    "Mt5DataPrinter",
    "Mt5RuntimeError",
]
