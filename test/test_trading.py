"""Tests for pdmt5.trading module."""

# pyright: reportPrivateUsage=false
# pyright: reportAttributeAccessIssue=false

from collections.abc import Generator
from types import ModuleType
from typing import NamedTuple

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

        # Mock order_calc_margin to return None for both margins
        mock_mt5_import.order_calc_margin.side_effect = [None, None]

        with pytest.raises(Mt5RuntimeError):
            client.calculate_minimum_order_margins("EURUSD")
