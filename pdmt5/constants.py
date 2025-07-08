"""MetaTrader5 constants for use with pdmt5."""

from enum import IntEnum


class Timeframe(IntEnum):
    """MetaTrader5 timeframe constants."""

    M1 = 1
    M2 = 2
    M3 = 3
    M4 = 4
    M5 = 5
    M6 = 6
    M10 = 10
    M12 = 12
    M15 = 15
    M20 = 20
    M30 = 30
    H1 = 16385
    H2 = 16386
    H3 = 16387
    H4 = 16388
    H6 = 16390
    H8 = 16392
    H12 = 16396
    D1 = 16408
    W1 = 32769
    MN1 = 49153


class TickFlag(IntEnum):
    """MetaTrader5 tick flag constants."""

    INFO = 1
    BID = 2
    ASK = 4
    LAST = 8
    VOLUME = 16
    ALL = 31


class OrderType(IntEnum):
    """MetaTrader5 order type constants."""

    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5
    BUY_STOP_LIMIT = 6
    SELL_STOP_LIMIT = 7
    CLOSE_BY = 8


class OrderState(IntEnum):
    """MetaTrader5 order state constants."""

    STARTED = 0
    PLACED = 1
    CANCELED = 2
    PARTIAL = 3
    FILLED = 4
    REJECTED = 5
    EXPIRED = 6
    REQUEST_ADD = 7
    REQUEST_MODIFY = 8
    REQUEST_CANCEL = 9


class OrderFilling(IntEnum):
    """MetaTrader5 order filling constants."""

    FOK = 0
    IOC = 1
    RETURN = 2


class OrderTime(IntEnum):
    """MetaTrader5 order time constants."""

    GTC = 0
    DAY = 1
    SPECIFIED = 2
    SPECIFIED_DAY = 3


class TradeAction(IntEnum):
    """MetaTrader5 trade action constants."""

    DEAL = 1
    PENDING = 5
    SLTP = 6
    MODIFY = 7
    REMOVE = 8
    CLOSE_BY = 10


class PositionType(IntEnum):
    """MetaTrader5 position type constants."""

    BUY = 0
    SELL = 1


class DealType(IntEnum):
    """MetaTrader5 deal type constants."""

    BUY = 0
    SELL = 1
    BALANCE = 2
    CREDIT = 3
    CHARGE = 4
    CORRECTION = 5
    BONUS = 6
    COMMISSION = 7
    COMMISSION_DAILY = 8
    COMMISSION_MONTHLY = 9
    COMMISSION_AGENT_DAILY = 10
    COMMISSION_AGENT_MONTHLY = 11
    INTEREST = 12
    BUY_CANCELED = 13
    SELL_CANCELED = 14
    DIVIDEND = 15
    DIVIDEND_FRANKED = 16
    TAX = 17


class DealEntry(IntEnum):
    """MetaTrader5 deal entry constants."""

    IN = 0
    OUT = 1
    INOUT = 2
    OUT_BY = 3


class DealReason(IntEnum):
    """MetaTrader5 deal reason constants."""

    CLIENT = 0
    MOBILE = 1
    WEB = 2
    EXPERT = 3
    SL = 4
    TP = 5
    SO = 6
    ROLLOVER = 7
    VMARGIN = 8
    GATEWAY = 9
    SIGNAL = 10
    SETTLEMENT = 11
    TRANSFER = 12
    SYNC = 13
    EXTERNAL_CLIENT = 14
    EXTERNAL_TOOL = 15
    EXTERNAL_CUSTOM = 16
    EXTERNAL_API = 17
    EXTERNAL_ADMIN = 18
    EXTERNAL_MANAGER = 19
    EXTERNAL_DEALER = 20
    EXTERNAL_RISK = 21
    EXTERNAL_SETTLEMENT = 22
    EXTERNAL_COMPLIANCE = 23
    EXTERNAL_GATEWAY = 24
    EXTERNAL_DATACENTER = 25
    UNKNOWN = 26


class SymbolCalcMode(IntEnum):
    """MetaTrader5 symbol calculation mode constants."""

    FOREX = 0
    FOREX_NO_LEVERAGE = 1
    FUTURES = 2
    CFD = 3
    CFD_LEVERAGE = 4
    CFD_INDEX = 5
    CFD_LEVERAGE_INDEX = 6
    EXCH_STOCKS = 32
    EXCH_FUTURES = 33
    EXCH_FUTURES_FORTS = 34
    EXCH_BONDS = 35
    EXCH_STOCKS_MOEX = 36
    EXCH_BONDS_MOEX = 37
    SERV_COLLATERAL = 64


class SymbolTradeMode(IntEnum):
    """MetaTrader5 symbol trade mode constants."""

    DISABLED = 0
    LONGONLY = 1
    SHORTONLY = 2
    CLOSEONLY = 3
    FULL = 4


class SymbolOrderMode(IntEnum):
    """MetaTrader5 symbol order mode constants."""

    MARKET = 1
    LIMIT = 2
    STOP = 4
    STOP_LIMIT = 8
    SL = 16
    TP = 32
    CLOSEBY = 64


class SymbolFillMode(IntEnum):
    """MetaTrader5 symbol fill mode constants."""

    FOK = 1
    IOC = 2
    RETURN = 4


class SymbolExpiration(IntEnum):
    """MetaTrader5 symbol expiration constants."""

    GTC = 1
    DAY = 2
    SPECIFIED = 4
    SPECIFIED_DAY = 8


class SymbolSwapMode(IntEnum):
    """MetaTrader5 symbol swap mode constants."""

    DISABLED = 0
    POINTS = 1
    SYMBOL_BASE = 2
    SYMBOL_MARGIN = 3
    CURRENCY_MARGIN = 4
    CURRENCY_DEPOSIT = 5
    PERCENT_OPEN = 6
    PERCENT_ANNUAL = 7
    PERCENT_ANNUAL_CURRENT = 8


class SymbolOption(IntEnum):
    """MetaTrader5 symbol option constants."""

    CALL = 0
    PUT = 1


class SymbolOptionRight(IntEnum):
    """MetaTrader5 symbol option right constants."""

    CALL = 0
    PUT = 1
