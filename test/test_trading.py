"""Tests for pdmt5.trading module."""

# pyright: reportPrivateUsage=false
# pyright: reportAttributeAccessIssue=false

from collections.abc import Generator
from types import ModuleType
from typing import NamedTuple

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from pdmt5.mt5 import Mt5RuntimeError
from pdmt5.trading import Mt5TradingClient, Mt5TradingError

# Rebuild models to ensure they are fully defined for testing
Mt5TradingClient.model_rebuild()


@pytest.fixture(autouse=True)
def mock_mt5_import(
    request: pytest.FixtureRequest,
    mocker: MockerFixture,
) -> Generator[ModuleType | None, None, None]:
    """Mock MetaTrader5 import for all tests.

    Yields:
        Mock object or None: Mock MetaTrader5 module for successful imports,
                            None for import error tests.
    """
    # Skip mocking for tests that explicitly test import errors
    if "initialize_import_error" in request.node.name:
        yield None
        return
    else:
        # Create a real module instance and add mock attributes to it
        mock_mt5 = ModuleType("mock_mt5")
        # Make it a MagicMock while preserving module type
        for attr in dir(mocker.MagicMock()):
            if not attr.startswith("__") or attr == "__call__":
                setattr(mock_mt5, attr, getattr(mocker.MagicMock(), attr))

        # Configure common mock attributes
        mock_mt5.initialize = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.shutdown = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.last_error = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.account_info = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.terminal_info = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbols_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbol_info = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbol_info_tick = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.positions_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_check = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_send = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_calc_margin = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_rates_from_pos = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_ticks_range = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_deals_get = mocker.MagicMock()  # type: ignore[attr-defined]

        # Trading-specific constants
        mock_mt5.TRADE_ACTION_DEAL = 1
        mock_mt5.ORDER_TYPE_BUY = 0
        mock_mt5.ORDER_TYPE_SELL = 1
        mock_mt5.POSITION_TYPE_BUY = 0
        mock_mt5.POSITION_TYPE_SELL = 1
        mock_mt5.ORDER_FILLING_IOC = 1
        mock_mt5.ORDER_FILLING_FOK = 2
        mock_mt5.ORDER_FILLING_RETURN = 3
        mock_mt5.ORDER_TIME_GTC = 0
        mock_mt5.TRADE_RETCODE_DONE = 10009
        mock_mt5.TRADE_RETCODE_TRADE_DISABLED = 10017
        mock_mt5.TRADE_RETCODE_MARKET_CLOSED = 10018
        mock_mt5.RES_S_OK = 1
        mock_mt5.DEAL_TYPE_BUY = 0
        mock_mt5.DEAL_TYPE_SELL = 1

        yield mock_mt5


class MockPositionInfo(NamedTuple):
    """Mock position info structure."""

    ticket: int
    symbol: str
    volume: float
    type: int
    time: int
    identifier: int
    reason: int
    price_open: float
    sl: float
    tp: float
    price_current: float
    swap: float
    profit: float
    magic: int
    comment: str
    external_id: str


class MockDealInfo(NamedTuple):
    """Mock deal info structure."""

    ticket: int
    type: int
    entry: bool
    time: int


@pytest.fixture
def mock_position_buy() -> MockPositionInfo:
    """Mock buy position."""
    return MockPositionInfo(
        ticket=12345,
        symbol="EURUSD",
        volume=0.1,
        type=0,  # POSITION_TYPE_BUY
        time=1234567890,
        identifier=12345,
        reason=0,
        price_open=1.2000,
        sl=0.0,
        tp=0.0,
        price_current=1.2050,
        swap=0.0,
        profit=5.0,
        magic=0,
        comment="test",
        external_id="",
    )


@pytest.fixture
def mock_position_sell() -> MockPositionInfo:
    """Mock sell position."""
    return MockPositionInfo(
        ticket=12346,
        symbol="GBPUSD",
        volume=0.2,
        type=1,  # POSITION_TYPE_SELL
        time=1234567890,
        identifier=12346,
        reason=0,
        price_open=1.3000,
        sl=0.0,
        tp=0.0,
        price_current=1.2950,
        swap=0.0,
        profit=10.0,
        magic=0,
        comment="test",
        external_id="",
    )


class TestMt5TradingError:
    """Tests for Mt5TradingError exception class."""

    def test_mt5_trading_error_inheritance(self) -> None:
        """Test that Mt5TradingError inherits from Mt5RuntimeError."""
        assert issubclass(Mt5TradingError, Mt5RuntimeError)

    def test_mt5_trading_error_creation(self) -> None:
        """Test Mt5TradingError creation with message."""
        message = "Trading operation failed"
        error = Mt5TradingError(message)
        assert str(error) == message
        assert isinstance(error, Mt5RuntimeError)

    def test_mt5_trading_error_empty_message(self) -> None:
        """Test Mt5TradingError creation with empty message."""
        error = Mt5TradingError("")
        assert not str(error)


class TestMt5TradingClient:
    """Tests for Mt5TradingClient class."""

    def test_client_initialization_default(self, mock_mt5_import: ModuleType) -> None:
        """Test client initialization with default parameters."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        assert client.order_filling_mode == "IOC"
        assert client.dry_run is False

    def test_client_initialization_custom(self, mock_mt5_import: ModuleType) -> None:
        """Test client initialization with custom parameters."""
        client = Mt5TradingClient(
            mt5=mock_mt5_import,
            order_filling_mode="FOK",
            dry_run=True,
        )
        assert client.order_filling_mode == "FOK"
        assert client.dry_run is True

    def test_client_initialization_invalid_filling_mode(
        self, mock_mt5_import: ModuleType
    ) -> None:
        """Test client initialization with invalid filling mode."""
        with pytest.raises(ValidationError):
            Mt5TradingClient(mt5=mock_mt5_import, order_filling_mode="INVALID")  # type: ignore[arg-type]

    def test_close_position_no_positions(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test close_position when no positions exist."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock empty positions
        mock_mt5_import.positions_get.return_value = []

        result = client.close_open_positions("EURUSD")

        assert result == {"EURUSD": []}
        mock_mt5_import.positions_get.assert_called_once_with(symbol="EURUSD")

    def test_close_position_with_positions(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
    ) -> None:
        """Test close_position with existing positions."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock positions
        mock_mt5_import.positions_get.return_value = [mock_position_buy]

        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009,
            "result": "success",
        }

        result = client.close_open_positions("EURUSD")

        assert len(result["EURUSD"]) == 1
        assert result["EURUSD"][0]["retcode"] == 10009
        mock_mt5_import.order_send.assert_called_once()

    def test_close_position_with_positions_dry_run(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
    ) -> None:
        """Test close_position with existing positions in dry run mode."""
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=True)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock positions
        mock_mt5_import.positions_get.return_value = [mock_position_buy]

        mock_mt5_import.order_check.return_value.retcode = 0
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 0,
            "result": "check_success",
        }

        result = client.close_open_positions("EURUSD")

        assert len(result["EURUSD"]) == 1
        assert result["EURUSD"][0]["retcode"] == 0
        mock_mt5_import.order_check.assert_called_once()
        mock_mt5_import.order_send.assert_not_called()

    def test_close_position_with_dry_run_override(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
    ) -> None:
        """Test close_position with dry_run parameter override."""
        # Client initialized with dry_run=False
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=False)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock positions
        mock_mt5_import.positions_get.return_value = [mock_position_buy]

        mock_mt5_import.order_check.return_value.retcode = 0
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 0,
            "result": "check_success",
        }

        # Override with dry_run=True
        result = client.close_open_positions("EURUSD", dry_run=True)

        assert len(result["EURUSD"]) == 1
        assert result["EURUSD"][0]["retcode"] == 0
        # Should use order_check instead of order_send
        mock_mt5_import.order_check.assert_called_once()
        mock_mt5_import.order_send.assert_not_called()

    def test_close_position_with_real_mode_override(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
    ) -> None:
        """Test close_position with real mode override."""
        # Client initialized with dry_run=True
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=True)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock positions
        mock_mt5_import.positions_get.return_value = [mock_position_buy]

        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009,
            "result": "send_success",
        }

        # Override with dry_run=False
        result = client.close_open_positions("EURUSD", dry_run=False)

        assert len(result["EURUSD"]) == 1
        assert result["EURUSD"][0]["retcode"] == 10009
        # Should use order_send instead of order_check
        mock_mt5_import.order_send.assert_called_once()
        mock_mt5_import.order_check.assert_not_called()

    def test_close_open_positions_all_symbols(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test close_open_positions for all symbols."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbols and positions
        mock_mt5_import.symbols_get.return_value = ["EURUSD", "GBPUSD"]
        mock_mt5_import.positions_get.return_value = []  # No positions

        result = client.close_open_positions()

        assert len(result) == 2
        assert "EURUSD" in result
        assert "GBPUSD" in result
        assert result["EURUSD"] == []
        assert result["GBPUSD"] == []

    def test_close_open_positions_specific_symbols(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test close_open_positions for specific symbols."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock empty positions
        mock_mt5_import.positions_get.return_value = []

        result = client.close_open_positions(["EURUSD"])

        assert len(result) == 1
        assert "EURUSD" in result
        assert result["EURUSD"] == []

    def test_close_open_positions_tuple_input(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test close_open_positions with tuple input."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock empty positions
        mock_mt5_import.positions_get.return_value = []

        result = client.close_open_positions(("EURUSD", "GBPUSD"))

        assert len(result) == 2
        assert "EURUSD" in result
        assert "GBPUSD" in result
        assert result["EURUSD"] == []
        assert result["GBPUSD"] == []

    def test_close_open_positions_with_kwargs(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
    ) -> None:
        """Test close_open_positions with additional kwargs."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock positions
        mock_mt5_import.positions_get.return_value = [mock_position_buy]

        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009,
            "result": "success",
        }

        # Pass custom kwargs
        result = client.close_open_positions(
            "EURUSD", comment="custom_close", magic=12345
        )

        assert len(result["EURUSD"]) == 1
        assert result["EURUSD"][0]["retcode"] == 10009

        # Check that kwargs were passed through
        call_args = mock_mt5_import.order_send.call_args[0][0]
        assert call_args["comment"] == "custom_close"
        assert call_args["magic"] == 12345

    def test_close_open_positions_with_kwargs_and_dry_run(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
    ) -> None:
        """Test close_open_positions with additional kwargs and dry_run override."""
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=False)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock positions
        mock_mt5_import.positions_get.return_value = [mock_position_buy]

        mock_mt5_import.order_check.return_value.retcode = 0
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 0,
            "result": "check_success",
        }

        # Pass custom kwargs with dry_run override
        result = client.close_open_positions(
            "EURUSD", dry_run=True, comment="custom_close", magic=12345
        )

        assert len(result["EURUSD"]) == 1
        assert result["EURUSD"][0]["retcode"] == 0

        # Check that kwargs were passed through to order_check
        call_args = mock_mt5_import.order_check.call_args[0][0]
        assert call_args["comment"] == "custom_close"
        assert call_args["magic"] == 12345
        mock_mt5_import.order_send.assert_not_called()

    def test_send_or_check_order_dry_run_success(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test send_or_check_order in dry run mode with success."""
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=True)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        # Mock successful order check
        mock_mt5_import.order_check.return_value.retcode = 0
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 0,
            "result": "check_success",
        }

        result = client.send_or_check_order(request)

        assert result["retcode"] == 0
        assert result["result"] == "check_success"
        mock_mt5_import.order_check.assert_called_once_with(request)

    def test_send_or_check_order_real_mode_success(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test send_or_check_order in real mode with success."""
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=False)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        # Mock successful order send
        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009,
            "result": "send_success",
        }

        result = client.send_or_check_order(request)

        assert result["retcode"] == 10009
        assert result["result"] == "send_success"
        mock_mt5_import.order_send.assert_called_once_with(request)

    def test_send_or_check_order_trade_disabled(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test send_or_check_order with trade disabled."""
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=False)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        # Mock trade disabled response
        mock_mt5_import.order_send.return_value.retcode = 10017
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10017,
            "comment": "Trade disabled",
        }

        result = client.send_or_check_order(request)

        assert result["retcode"] == 10017

    def test_send_or_check_order_market_closed(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test send_or_check_order with market closed."""
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=False)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        # Mock market closed response
        mock_mt5_import.order_send.return_value.retcode = 10018
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10018,
            "comment": "Market closed",
        }

        result = client.send_or_check_order(request)

        assert result["retcode"] == 10018

    def test_send_or_check_order_failure(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test send_or_check_order with failure."""
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=False)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        # Mock failure response
        mock_mt5_import.order_send.return_value.retcode = 10004
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10004,
            "comment": "Invalid request",
        }

        with pytest.raises(Mt5TradingError, match=r"order_send\(\) failed and aborted"):
            client.send_or_check_order(request)

    def test_send_or_check_order_dry_run_failure(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test send_or_check_order in dry run mode with failure."""
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=True)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        # Mock failure response
        mock_mt5_import.order_check.return_value.retcode = 10004
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 10004,
            "comment": "Invalid request",
        }

        with pytest.raises(
            Mt5TradingError, match=r"order_check\(\) failed and aborted"
        ):
            client.send_or_check_order(request)

    def test_send_or_check_order_dry_run_override(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test send_or_check_order with dry_run parameter override."""
        # Client initialized with dry_run=False
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=False)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        # Mock successful order check
        mock_mt5_import.order_check.return_value.retcode = 0
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 0,
            "result": "check_success",
        }

        # Override with dry_run=True
        result = client.send_or_check_order(request, dry_run=True)

        assert result["retcode"] == 0
        assert result["result"] == "check_success"
        # Should call order_check, not order_send
        mock_mt5_import.order_check.assert_called_once_with(request)
        mock_mt5_import.order_send.assert_not_called()

    def test_send_or_check_order_real_mode_override(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test send_or_check_order with real mode override."""
        # Client initialized with dry_run=True
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=True)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        # Mock successful order send
        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009,
            "result": "send_success",
        }

        # Override with dry_run=False
        result = client.send_or_check_order(request, dry_run=False)

        assert result["retcode"] == 10009
        assert result["result"] == "send_success"
        # Should call order_send, not order_check
        mock_mt5_import.order_send.assert_called_once_with(request)
        mock_mt5_import.order_check.assert_not_called()

    def test_order_filling_mode_constants(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
    ) -> None:
        """Test that order filling mode constants are used correctly."""
        client = Mt5TradingClient(mt5=mock_mt5_import, order_filling_mode="FOK")
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock positions
        mock_mt5_import.positions_get.return_value = [mock_position_buy]

        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009
        }

        client.close_open_positions("EURUSD")

        # Verify that ORDER_FILLING_FOK was used
        call_args = mock_mt5_import.order_send.call_args[0][0]
        assert call_args["type_filling"] == mock_mt5_import.ORDER_FILLING_FOK

    def test_position_type_handling(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
        mock_position_sell: MockPositionInfo,
    ) -> None:
        """Test that position types are handled correctly for closing."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Test buy position -> sell order
        mock_mt5_import.positions_get.return_value = [mock_position_buy]

        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009
        }

        client.close_open_positions("EURUSD")

        # Buy position should result in sell order
        call_args = mock_mt5_import.order_send.call_args[0][0]
        assert call_args["type"] == mock_mt5_import.ORDER_TYPE_SELL

        # Test sell position -> buy order
        mock_mt5_import.positions_get.return_value = [mock_position_sell]

        mock_mt5_import.order_send.reset_mock()

        client.close_open_positions("GBPUSD")

        # Sell position should result in buy order
        call_args = mock_mt5_import.order_send.call_args[0][0]
        assert call_args["type"] == mock_mt5_import.ORDER_TYPE_BUY

    def test_fetch_and_close_position_with_dry_run(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
        mock_position_sell: MockPositionInfo,
    ) -> None:
        """Test _fetch_and_close_position with dry_run parameter."""
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=False)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Test with multiple positions and dry_run override
        mock_mt5_import.positions_get.return_value = [
            mock_position_buy,
            mock_position_sell,
        ]

        mock_mt5_import.order_check.return_value.retcode = 0
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 0,
            "result": "check_success",
        }

        # Call internal method directly with dry_run=True
        result = client._fetch_and_close_position(symbol="EURUSD", dry_run=True)

        assert len(result) == 2
        assert all(r["retcode"] == 0 for r in result)
        assert mock_mt5_import.order_check.call_count == 2
        mock_mt5_import.order_send.assert_not_called()

    def test_fetch_and_close_position_inherits_instance_dry_run(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,
    ) -> None:
        """Test _fetch_and_close_position inherits instance dry_run if not given."""
        # Client initialized with dry_run=True
        client = Mt5TradingClient(mt5=mock_mt5_import, dry_run=True)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        mock_mt5_import.positions_get.return_value = [mock_position_buy]

        mock_mt5_import.order_check.return_value.retcode = 0
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 0,
            "result": "check_success",
        }

        # Call without specifying dry_run - should use instance's dry_run=True
        result = client._fetch_and_close_position(symbol="EURUSD")

        assert len(result) == 1
        assert result[0]["retcode"] == 0
        mock_mt5_import.order_check.assert_called_once()
        mock_mt5_import.order_send.assert_not_called()

    def test_calculate_minimum_order_margins_success(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test successful calculation of minimum order margins."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbol info
        mock_mt5_import.symbol_info.return_value._asdict.return_value = {
            "volume_min": 0.01,
            "name": "EURUSD",
        }

        # Mock symbol tick info
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "ask": 1.1000,
            "bid": 1.0998,
        }

        # Mock order_calc_margin to return successful results
        mock_mt5_import.order_calc_margin.side_effect = [100.5, 99.8]

        result = client.calculate_minimum_order_margins("EURUSD")

        assert result == {"ask": 100.5, "bid": 99.8}
        assert mock_mt5_import.order_calc_margin.call_count == 2

        # Verify first call (buy order)
        first_call = mock_mt5_import.order_calc_margin.call_args_list[0]
        assert first_call[0][0] == mock_mt5_import.ORDER_TYPE_BUY  # action
        assert first_call[0][1] == "EURUSD"  # symbol
        assert first_call[0][2] == 0.01  # volume
        assert first_call[0][3] == 1.1000  # price

        # Verify second call (sell order)
        second_call = mock_mt5_import.order_calc_margin.call_args_list[1]
        assert second_call[0][0] == mock_mt5_import.ORDER_TYPE_SELL  # action
        assert second_call[0][1] == "EURUSD"  # symbol
        assert second_call[0][2] == 0.01  # volume
        assert second_call[0][3] == 1.0998  # price

    def test_calculate_minimum_order_margins_failure_ask(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test failed calculation of minimum order margins - ask margin fails."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbol info
        mock_mt5_import.symbol_info.return_value._asdict.return_value = {
            "volume_min": 0.01,
            "name": "EURUSD",
        }

        # Mock symbol tick info
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "ask": 1.1000,
            "bid": 1.0998,
        }

        # Mock order_calc_margin to return None for ask margin
        mock_mt5_import.order_calc_margin.side_effect = [None, 99.8]

        with pytest.raises(Mt5RuntimeError):
            client.calculate_minimum_order_margins("EURUSD")

    def test_calculate_minimum_order_margins_failure_bid(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test failed calculation of minimum order margins - bid margin fails."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbol info
        mock_mt5_import.symbol_info.return_value._asdict.return_value = {
            "volume_min": 0.01,
            "name": "EURUSD",
        }

        # Mock symbol tick info
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "ask": 1.1000,
            "bid": 1.0998,
        }

        # Mock order_calc_margin to return None for bid margin
        mock_mt5_import.order_calc_margin.side_effect = [100.5, None]

        with pytest.raises(Mt5RuntimeError):
            client.calculate_minimum_order_margins("EURUSD")

    def test_calculate_minimum_order_margins_failure_both(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test failed calculation of minimum order margins - both margins fail."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbol info
        mock_mt5_import.symbol_info.return_value._asdict.return_value = {
            "volume_min": 0.01,
            "name": "EURUSD",
        }

        # Mock symbol tick info
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "ask": 1.1000,
            "bid": 1.0998,
        }

        # Mock order_calc_margin to return 0.0 for both margins (indicates failure)
        mock_mt5_import.order_calc_margin.side_effect = [0.0, 0.0]

        with pytest.raises(Mt5TradingError):
            client.calculate_minimum_order_margins("EURUSD")

    def test_calculate_spread_ratio(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test calculation of spread ratio."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbol tick info
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "ask": 1.1002,
            "bid": 1.1000,
        }

        result = client.calculate_spread_ratio("EURUSD")

        # Expected calculation: (1.1002 - 1.1000) / (1.1002 + 1.1000) * 2
        expected = (1.1002 - 1.1000) / (1.1002 + 1.1000) * 2
        assert result == expected
        mock_mt5_import.symbol_info_tick.assert_called_once_with("EURUSD")

    def test_fetch_latest_rates_as_df_success(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test successful fetching of rate data as DataFrame."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock TIMEFRAME constant
        mock_mt5_import.TIMEFRAME_M1 = 1

        # Create structured array that mimics MT5 rates structure
        rates_dtype = np.dtype([
            ("time", "i8"),
            ("open", "f8"),
            ("high", "f8"),
            ("low", "f8"),
            ("close", "f8"),
            ("tick_volume", "i8"),
            ("spread", "i4"),
            ("real_volume", "i8"),
        ])

        mock_rates_data = np.array(
            [
                (1234567890, 1.1000, 1.1010, 1.0990, 1.1005, 100, 2, 10000),
            ],
            dtype=rates_dtype,
        )

        mock_mt5_import.copy_rates_from_pos.return_value = mock_rates_data

        result = client.fetch_latest_rates_as_df("EURUSD", granularity="M1", count=10)

        assert result is not None
        mock_mt5_import.copy_rates_from_pos.assert_called_once_with(
            "EURUSD",  # symbol
            1,  # timeframe
            0,  # start_pos
            10,  # count
        )

    def test_fetch_latest_rates_as_df_invalid_granularity(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test fetching rate data with invalid granularity."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Ensure the attribute doesn't exist for invalid granularity
        if hasattr(mock_mt5_import, "TIMEFRAME_INVALID"):
            delattr(mock_mt5_import, "TIMEFRAME_INVALID")

        with pytest.raises(
            Mt5TradingError,
            match="MetaTrader5 does not support the given granularity: INVALID",
        ):
            client.fetch_latest_rates_as_df("EURUSD", granularity="INVALID")

    def test_fetch_latest_ticks_as_df(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test fetching tick data as DataFrame."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbol tick info with time
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "time": 1234567890,
            "ask": 1.1002,
            "bid": 1.1000,
        }

        # Mock copy ticks flag
        mock_mt5_import.COPY_TICKS_ALL = 1

        # Create structured array that mimics MT5 ticks structure
        ticks_dtype = np.dtype([
            ("time", "i8"),
            ("bid", "f8"),
            ("ask", "f8"),
            ("last", "f8"),
            ("volume", "i8"),
            ("time_msc", "i8"),
            ("flags", "i4"),
            ("volume_real", "f8"),
        ])

        mock_ticks_data = np.array(
            [
                (1234567890, 1.1000, 1.1002, 1.1001, 100, 1234567890000, 0, 100.0),
            ],
            dtype=ticks_dtype,
        )

        mock_mt5_import.copy_ticks_range.return_value = mock_ticks_data

        result = client.fetch_latest_ticks_as_df("EURUSD", seconds=60)

        assert result is not None
        # Verify the method was called
        mock_mt5_import.symbol_info_tick.assert_called_once_with("EURUSD")

        # Verify copy_ticks_range was called with correct arguments
        call_args = mock_mt5_import.copy_ticks_range.call_args[0]
        assert call_args[0] == "EURUSD"  # symbol
        assert call_args[3] == 1  # flags (COPY_TICKS_ALL)

        # Verify result has the expected structure
        assert len(result) == 1
        # time_msc is likely the index, not a column
        assert "bid" in result.columns
        assert "ask" in result.columns
        assert "last" in result.columns
        assert "volume" in result.columns

    def test_collect_entry_deals_as_df(self, mock_mt5_import: ModuleType) -> None:
        """Test collecting entry deals as DataFrame."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbol tick info
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "time": 1234567890,
        }

        # Create mock deal objects
        mock_deals = [
            # BUY, entry
            MockDealInfo(ticket=1001, type=0, entry=True, time=1234567890),
            # SELL, entry
            MockDealInfo(ticket=1002, type=1, entry=True, time=1234567891),
            # other type, entry
            MockDealInfo(ticket=1003, type=2, entry=True, time=1234567892),
            # BUY, not entry
            MockDealInfo(ticket=1004, type=0, entry=False, time=1234567893),
            # SELL, entry
            MockDealInfo(ticket=1005, type=1, entry=True, time=1234567894),
        ]

        # Mock history_deals_get to return the mock deals
        mock_mt5_import.history_deals_get.return_value = mock_deals

        result = client.collect_entry_deals_as_df("EURUSD", history_seconds=3600)

        # Verify symbol_info_tick was called
        mock_mt5_import.symbol_info_tick.assert_called_once_with("EURUSD")

        # Verify history_deals_get was called with correct parameters
        mock_mt5_import.history_deals_get.assert_called_once()
        call_args = mock_mt5_import.history_deals_get.call_args
        # Check positional args (date_from, date_to)
        assert len(call_args[0]) == 2
        date_from, date_to = call_args[0]
        # Compare timestamps to avoid timezone issues
        if isinstance(date_from, pd.Timestamp):
            date_from_ts = date_from.timestamp()
        else:
            date_from_ts = date_from.timestamp()
        if isinstance(date_to, pd.Timestamp):
            date_to_ts = date_to.timestamp()
        else:
            date_to_ts = date_to.timestamp()

        expected_from_ts = 1234567890 - 3600
        expected_to_ts = 1234567890 + 3600
        assert abs(date_from_ts - expected_from_ts) < 1  # Allow 1 second tolerance
        assert abs(date_to_ts - expected_to_ts) < 1  # Allow 1 second tolerance
        # Check group parameter
        assert call_args[1]["group"] == "*EURUSD*"

        # Verify filtered results - should only have entry deals with BUY/SELL types
        assert len(result) == 3  # tickets 1001, 1002, 1005
        assert 1001 in result.index  # entry=True, type=BUY
        assert 1002 in result.index  # entry=True, type=SELL
        assert 1003 not in result.index  # entry=True but type=2 (not BUY/SELL)
        assert 1004 not in result.index  # entry=False
        assert 1005 in result.index  # entry=True, type=SELL

    def test_collect_entry_deals_as_df_custom_parameters(
        self, mock_mt5_import: ModuleType
    ) -> None:
        """Test collecting entry deals with custom parameters."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbol tick info
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "time": 1234567890,
        }

        # Mock empty deals
        mock_mt5_import.history_deals_get.return_value = []

        result = client.collect_entry_deals_as_df(
            "GBPUSD", history_seconds=7200, index_keys="time"
        )

        # Verify parameters were passed through
        mock_mt5_import.history_deals_get.assert_called_once()
        call_args = mock_mt5_import.history_deals_get.call_args
        # Check positional args
        date_from, date_to = call_args[0]

        # Compare timestamps to avoid timezone issues
        if isinstance(date_from, pd.Timestamp):
            date_from_ts = date_from.timestamp()
        else:
            date_from_ts = date_from.timestamp()
        if isinstance(date_to, pd.Timestamp):
            date_to_ts = date_to.timestamp()
        else:
            date_to_ts = date_to.timestamp()

        expected_from_ts = 1234567890 - 7200
        expected_to_ts = 1234567890 + 7200
        assert abs(date_from_ts - expected_from_ts) < 1  # Allow 1 second tolerance
        assert abs(date_to_ts - expected_to_ts) < 1  # Allow 1 second tolerance
        # Check group parameter
        assert call_args[1]["group"] == "*GBPUSD*"

        # Result should be empty DataFrame
        assert len(result) == 0

    def test_collect_entry_deals_as_df_no_index(
        self, mock_mt5_import: ModuleType
    ) -> None:
        """Test collecting entry deals without index."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock symbol tick info
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "time": 1234567890,
        }

        # Create mock deal objects
        mock_deals = [
            # BUY, entry
            MockDealInfo(ticket=1001, type=0, entry=True, time=1234567890),
            # SELL, entry
            MockDealInfo(ticket=1002, type=1, entry=True, time=1234567891),
        ]

        # Mock history_deals_get to return the mock deals
        mock_mt5_import.history_deals_get.return_value = mock_deals

        result = client.collect_entry_deals_as_df(
            "USDJPY", history_seconds=1800, index_keys=None
        )

        # Verify results
        assert len(result) == 2
        # When index_keys is None, result should not have ticket as index
        assert result.index.name is None
        # Check that both deals are in the result
        assert 1001 in result["ticket"].to_numpy()
        assert 1002 in result["ticket"].to_numpy()

    def test_fetch_positions_with_metrics_as_df_empty(
        self, mock_mt5_import: ModuleType
    ) -> None:
        """Test fetching positions with metrics when no positions exist."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Mock empty positions
        mock_mt5_import.positions_get.return_value = []

        result = client.fetch_positions_with_metrics_as_df("EURUSD")

        # Should return empty DataFrame
        assert result.empty
        assert isinstance(result, pd.DataFrame)

    def test_fetch_positions_with_metrics_as_df_with_positions(
        self,
        mock_mt5_import: ModuleType,
        mock_position_buy: MockPositionInfo,  # noqa: ARG002
        mocker: MockerFixture,
    ) -> None:
        """Test fetching positions with metrics when positions exist."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        client.initialize()

        # Create a mock position that returns the right data when converted
        mock_position = mocker.MagicMock()
        mock_position._asdict.return_value = {
            "ticket": 12345,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 0,  # POSITION_TYPE_BUY
            "time": 1234567890,  # This will be converted by decorator
            "price_open": 1.2,
            "price_current": 1.205,
            "profit": 5.0,
            "sl": 0.0,
            "tp": 0.0,
            "identifier": 12345,
            "reason": 0,
            "swap": 0.0,
            "magic": 0,
            "comment": "test",
            "external_id": "",
        }
        mock_mt5_import.positions_get.return_value = [mock_position]

        # Mock symbol tick info
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "time": pd.Timestamp(
                "2009-02-14 00:31:30"
            ),  # tz-naive to match decorated positions
            "ask": 1.1002,
            "bid": 1.1000,
        }

        # Mock order calc margin
        mock_mt5_import.order_calc_margin.return_value = 1000.0

        result = client.fetch_positions_with_metrics_as_df("EURUSD")

        # Verify DataFrame is not empty and has expected columns
        assert not result.empty
        assert isinstance(result, pd.DataFrame)
        assert "elapsed_seconds" in result.columns
        assert "underlier_profit_ratio" in result.columns
        assert "buy" in result.columns
        assert "sell" in result.columns
        assert "margin" in result.columns
        assert "signed_volume" in result.columns
        assert "signed_margin" in result.columns

        # Verify calculations
        row = result.iloc[0]
        assert row["buy"]  # mock_position_buy has type=0 (BUY)
        assert not row["sell"]
        assert row["margin"] == 100.0  # 0.1 volume * 1000 margin
        assert row["signed_volume"] == 0.1  # buy position has positive volume
        assert row["signed_margin"] == 100.0  # buy position has positive margin

        # Verify order_calc_margin was called twice (ask and bid)
        assert mock_mt5_import.order_calc_margin.call_count == 2
