"""pdmt5: Pandas-based data handler for MetaTrader 5."""

from importlib.metadata import version

from .constants import (
    DealEntry,
    DealReason,
    DealType,
    OrderFilling,
    OrderState,
    OrderTime,
    OrderType,
    PositionType,
    SymbolCalcMode,
    SymbolExpiration,
    SymbolFillMode,
    SymbolOption,
    SymbolOptionRight,
    SymbolOrderMode,
    SymbolSwapMode,
    SymbolTradeMode,
    TickFlag,
    Timeframe,
    TradeAction,
)
from .manipulator import Mt5Config, Mt5DataClient, Mt5Error

__version__ = version(__package__) if __package__ else None

__all__ = [
    "DealEntry",
    "DealReason",
    "DealType",
    "Mt5Config",
    "Mt5DataClient",
    "Mt5Error",
    "OrderFilling",
    "OrderState",
    "OrderTime",
    "OrderType",
    "PositionType",
    "SymbolCalcMode",
    "SymbolExpiration",
    "SymbolFillMode",
    "SymbolOption",
    "SymbolOptionRight",
    "SymbolOrderMode",
    "SymbolSwapMode",
    "SymbolTradeMode",
    "TickFlag",
    "Timeframe",
    "TradeAction",
]
