"""pdmt5: Pandas-based data handler for MetaTrader 5."""

from importlib.metadata import version

from .manipulator import Mt5Config, Mt5DataClient, Mt5RuntimeError

__version__ = version(__package__) if __package__ else None

__all__ = [
    "Mt5Config",
    "Mt5DataClient",
    "Mt5RuntimeError",
]
