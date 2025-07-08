"""Tests for pdmt5.constants module."""

from pdmt5.constants import (
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


class TestTimeframe:
    """Test Timeframe constants."""

    def test_minute_timeframes(self) -> None:
        """Test minute timeframes."""
        assert Timeframe.M1 == 1
        assert Timeframe.M5 == 5
        assert Timeframe.M15 == 15
        assert Timeframe.M30 == 30

    def test_hour_timeframes(self) -> None:
        """Test hour timeframes."""
        assert Timeframe.H1 == 16385
        assert Timeframe.H4 == 16388
        assert Timeframe.H12 == 16396

    def test_day_timeframes(self) -> None:
        """Test day timeframes."""
        assert Timeframe.D1 == 16408
        assert Timeframe.W1 == 32769
        assert Timeframe.MN1 == 49153


class TestTickFlag:
    """Test TickFlag constants."""

    def test_tick_flags(self) -> None:
        """Test tick flag values."""
        assert TickFlag.INFO == 1
        assert TickFlag.BID == 2
        assert TickFlag.ASK == 4
        assert TickFlag.LAST == 8
        assert TickFlag.VOLUME == 16
        assert TickFlag.ALL == 31


class TestOrderType:
    """Test OrderType constants."""

    def test_order_types(self) -> None:
        """Test order type values."""
        assert OrderType.BUY == 0
        assert OrderType.SELL == 1
        assert OrderType.BUY_LIMIT == 2
        assert OrderType.SELL_LIMIT == 3
        assert OrderType.BUY_STOP == 4
        assert OrderType.SELL_STOP == 5
        assert OrderType.BUY_STOP_LIMIT == 6
        assert OrderType.SELL_STOP_LIMIT == 7
        assert OrderType.CLOSE_BY == 8


class TestOrderState:
    """Test OrderState constants."""

    def test_order_states(self) -> None:
        """Test order state values."""
        assert OrderState.STARTED == 0
        assert OrderState.PLACED == 1
        assert OrderState.CANCELED == 2
        assert OrderState.PARTIAL == 3
        assert OrderState.FILLED == 4
        assert OrderState.REJECTED == 5
        assert OrderState.EXPIRED == 6


class TestOrderFilling:
    """Test OrderFilling constants."""

    def test_order_filling(self) -> None:
        """Test order filling values."""
        assert OrderFilling.FOK == 0
        assert OrderFilling.IOC == 1
        assert OrderFilling.RETURN == 2


class TestOrderTime:
    """Test OrderTime constants."""

    def test_order_time(self) -> None:
        """Test order time values."""
        assert OrderTime.GTC == 0
        assert OrderTime.DAY == 1
        assert OrderTime.SPECIFIED == 2
        assert OrderTime.SPECIFIED_DAY == 3


class TestTradeAction:
    """Test TradeAction constants."""

    def test_trade_actions(self) -> None:
        """Test trade action values."""
        assert TradeAction.DEAL == 1
        assert TradeAction.PENDING == 5
        assert TradeAction.SLTP == 6
        assert TradeAction.MODIFY == 7
        assert TradeAction.REMOVE == 8
        assert TradeAction.CLOSE_BY == 10


class TestPositionType:
    """Test PositionType constants."""

    def test_position_types(self) -> None:
        """Test position type values."""
        assert PositionType.BUY == 0
        assert PositionType.SELL == 1


class TestDealType:
    """Test DealType constants."""

    def test_deal_types(self) -> None:
        """Test deal type values."""
        assert DealType.BUY == 0
        assert DealType.SELL == 1
        assert DealType.BALANCE == 2
        assert DealType.CREDIT == 3
        assert DealType.COMMISSION == 7
        assert DealType.INTEREST == 12
        assert DealType.DIVIDEND == 15
        assert DealType.TAX == 17


class TestDealEntry:
    """Test DealEntry constants."""

    def test_deal_entries(self) -> None:
        """Test deal entry values."""
        assert DealEntry.IN == 0
        assert DealEntry.OUT == 1
        assert DealEntry.INOUT == 2
        assert DealEntry.OUT_BY == 3


class TestDealReason:
    """Test DealReason constants."""

    def test_deal_reasons(self) -> None:
        """Test deal reason values."""
        assert DealReason.CLIENT == 0
        assert DealReason.MOBILE == 1
        assert DealReason.WEB == 2
        assert DealReason.EXPERT == 3
        assert DealReason.SL == 4
        assert DealReason.TP == 5
        assert DealReason.SO == 6
        assert DealReason.UNKNOWN == 26


class TestSymbolConstants:
    """Test Symbol-related constants."""

    def test_symbol_calc_mode(self) -> None:
        """Test symbol calculation mode values."""
        assert SymbolCalcMode.FOREX == 0
        assert SymbolCalcMode.FUTURES == 2
        assert SymbolCalcMode.CFD == 3
        assert SymbolCalcMode.EXCH_STOCKS == 32

    def test_symbol_trade_mode(self) -> None:
        """Test symbol trade mode values."""
        assert SymbolTradeMode.DISABLED == 0
        assert SymbolTradeMode.LONGONLY == 1
        assert SymbolTradeMode.SHORTONLY == 2
        assert SymbolTradeMode.CLOSEONLY == 3
        assert SymbolTradeMode.FULL == 4

    def test_symbol_order_mode(self) -> None:
        """Test symbol order mode values."""
        assert SymbolOrderMode.MARKET == 1
        assert SymbolOrderMode.LIMIT == 2
        assert SymbolOrderMode.STOP == 4
        assert SymbolOrderMode.STOP_LIMIT == 8
        assert SymbolOrderMode.SL == 16
        assert SymbolOrderMode.TP == 32
        assert SymbolOrderMode.CLOSEBY == 64

    def test_symbol_fill_mode(self) -> None:
        """Test symbol fill mode values."""
        assert SymbolFillMode.FOK == 1
        assert SymbolFillMode.IOC == 2
        assert SymbolFillMode.RETURN == 4

    def test_symbol_expiration(self) -> None:
        """Test symbol expiration values."""
        assert SymbolExpiration.GTC == 1
        assert SymbolExpiration.DAY == 2
        assert SymbolExpiration.SPECIFIED == 4
        assert SymbolExpiration.SPECIFIED_DAY == 8

    def test_symbol_swap_mode(self) -> None:
        """Test symbol swap mode values."""
        assert SymbolSwapMode.DISABLED == 0
        assert SymbolSwapMode.POINTS == 1
        assert SymbolSwapMode.SYMBOL_BASE == 2
        assert SymbolSwapMode.SYMBOL_MARGIN == 3
        assert SymbolSwapMode.CURRENCY_MARGIN == 4
        assert SymbolSwapMode.CURRENCY_DEPOSIT == 5
        assert SymbolSwapMode.PERCENT_OPEN == 6
        assert SymbolSwapMode.PERCENT_ANNUAL == 7
        assert SymbolSwapMode.PERCENT_ANNUAL_CURRENT == 8

    def test_symbol_option(self) -> None:
        """Test symbol option values."""
        assert SymbolOption.CALL == 0
        assert SymbolOption.PUT == 1

    def test_symbol_option_right(self) -> None:
        """Test symbol option right values."""
        assert SymbolOptionRight.CALL == 0
        assert SymbolOptionRight.PUT == 1
