"""pdmt5: Pandas-based data handler for MetaTrader 5."""

from importlib.metadata import version

from .client import Mt5Client
from .exception import Mt5RuntimeError
from .manipulator import Mt5Config, Mt5DataClient
from .printer import Mt5DataPrinter

__version__ = version(__package__) if __package__ else None

__all__ = [
    "Mt5Client",
    "Mt5Config",
    "Mt5DataClient",
    "Mt5DataPrinter",
    "Mt5RuntimeError",
]
