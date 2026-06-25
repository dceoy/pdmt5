"""Tests for pdmt5.trading module."""

from collections.abc import Generator
from types import ModuleType
from typing import Any, Literal, cast

import numpy as np
import pytest
from pytest_mock import MockerFixture

from pdmt5.mt5 import Mt5RuntimeError
from pdmt5.trading import Mt5TradingClient, Mt5TradingError
from tests.helpers import create_mock_mt5_module

# Rebuild models to ensure they are fully defined for testing
Mt5TradingClient.model_rebuild()

_MT5_METHODS = (
    "initialize",
    "shutdown",
    "last_error",
    "account_info",
    "terminal_info",
    "symbols_get",
    "symbol_info",
    "symbol_info_tick",
    "positions_get",
    "order_check",
    "order_send",
    "order_calc_margin",
    "copy_rates_from_pos",
    "copy_ticks_range",
)

_MT5_CONSTANTS = {
    "RES_S_OK": 1,
    "TRADE_ACTION_DEAL": 1,
    "ORDER_TYPE_BUY": 0,
    "ORDER_TYPE_SELL": 1,
    "ORDER_FILLING_IOC": 1,
    "ORDER_FILLING_FOK": 2,
    "ORDER_FILLING_RETURN": 3,
    "ORDER_TIME_GTC": 0,
    "TRADE_RETCODE_REQUOTE": 10004,
    "TRADE_RETCODE_REJECT": 10006,
    "TRADE_RETCODE_CANCEL": 10007,
    "TRADE_RETCODE_PLACED": 10008,
    "TRADE_RETCODE_DONE": 10009,
    "TRADE_RETCODE_DONE_PARTIAL": 10010,
    "TRADE_RETCODE_ERROR": 10011,
    "TRADE_RETCODE_TIMEOUT": 10012,
    "TRADE_RETCODE_INVALID": 10013,
    "TRADE_RETCODE_INVALID_VOLUME": 10014,
    "TRADE_RETCODE_INVALID_PRICE": 10015,
    "TRADE_RETCODE_INVALID_STOPS": 10016,
    "TRADE_RETCODE_TRADE_DISABLED": 10017,
    "TRADE_RETCODE_MARKET_CLOSED": 10018,
    "TRADE_RETCODE_NO_MONEY": 10019,
    "TRADE_RETCODE_PRICE_CHANGED": 10020,
    "TRADE_RETCODE_PRICE_OFF": 10021,
    "TRADE_RETCODE_INVALID_EXPIRATION": 10022,
    "TRADE_RETCODE_ORDER_CHANGED": 10023,
    "TRADE_RETCODE_TOO_MANY_REQUESTS": 10024,
    "TRADE_RETCODE_NO_CHANGES": 10025,
    "TRADE_RETCODE_SERVER_DISABLES_AT": 10026,
    "TRADE_RETCODE_CLIENT_DISABLES_AT": 10027,
    "TRADE_RETCODE_LOCKED": 10028,
    "TRADE_RETCODE_FROZEN": 10029,
    "TRADE_RETCODE_INVALID_FILL": 10030,
    "TRADE_RETCODE_CONNECTION": 10031,
    "TRADE_RETCODE_ONLY_REAL": 10032,
    "TRADE_RETCODE_LIMIT_ORDERS": 10033,
    "TRADE_RETCODE_LIMIT_VOLUME": 10034,
    "TRADE_RETCODE_INVALID_ORDER": 10035,
    "TRADE_RETCODE_POSITION_CLOSED": 10036,
    "TRADE_RETCODE_INVALID_CLOSE_VOLUME": 10038,
    "TRADE_RETCODE_CLOSE_ORDER_EXIST": 10039,
    "TRADE_RETCODE_LIMIT_POSITIONS": 10040,
    "TRADE_RETCODE_REJECT_CANCEL": 10041,
    "TRADE_RETCODE_LONG_ONLY": 10042,
    "TRADE_RETCODE_SHORT_ONLY": 10043,
    "TRADE_RETCODE_CLOSE_ONLY": 10044,
    "TRADE_RETCODE_FIFO_CLOSE": 10045,
    "TRADE_RETCODE_HEDGE_PROHIBITED": 10046,
}


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
    node_name = cast("Any", request).node.name
    if "initialize_import_error" in node_name:
        yield None
        return

    yield create_mock_mt5_module(
        mocker,
        methods=_MT5_METHODS,
        constants=_MT5_CONSTANTS,
    )


def create_initialized_client(mock_mt5_import: ModuleType) -> Mt5TradingClient:
    """Create an initialized trading client."""
    mock_mt5_import.initialize.return_value = True
    client = Mt5TradingClient(mt5=mock_mt5_import)
    client.initialize()
    return client


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
        assert isinstance(client, Mt5TradingClient)

    def test_client_initialization_custom(self, mock_mt5_import: ModuleType) -> None:
        """Test client initialization with custom parameters."""
        client = Mt5TradingClient(mt5=mock_mt5_import)
        assert isinstance(client, Mt5TradingClient)

    def test_send_or_check_order_dry_run_success(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test _send_or_check_order in dry run mode with success."""
        client = create_initialized_client(mock_mt5_import)

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        mock_mt5_import.order_check.return_value.retcode = 0
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 0,
            "result": "check_success",
        }

        result = client._send_or_check_order(  # type: ignore[reportPrivateUsage]
            request,
            dry_run=True,
        )

        assert result["retcode"] == 0
        assert result["result"] == "check_success"
        mock_mt5_import.order_check.assert_called_once_with(request)

    def test_send_or_check_order_real_mode_success(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test _send_or_check_order in real mode with success."""
        client = create_initialized_client(mock_mt5_import)

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009,
            "result": "send_success",
        }

        result = client._send_or_check_order(  # type: ignore[reportPrivateUsage]
            request
        )

        assert result["retcode"] == 10009
        assert result["result"] == "send_success"
        mock_mt5_import.order_send.assert_called_once_with(request)

    @pytest.mark.parametrize(
        ("retcode", "comment"),
        [
            (10017, "Trade disabled"),
            (10018, "Market closed"),
            (10025, "No changes"),
        ],
    )
    def test_send_or_check_order_non_error_retcodes(
        self, mock_mt5_import: ModuleType, retcode: int, comment: str
    ) -> None:
        """Test _send_or_check_order with non-error retcodes."""
        client = create_initialized_client(mock_mt5_import)

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        mock_mt5_import.order_send.return_value.retcode = retcode
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": retcode,
            "comment": comment,
        }

        result = client._send_or_check_order(  # type: ignore[reportPrivateUsage]
            request
        )

        assert result["retcode"] == retcode

    def test_send_or_check_order_failure(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test _send_or_check_order with failure."""
        client = create_initialized_client(mock_mt5_import)

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        mock_mt5_import.order_send.return_value.retcode = 10006
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10006,
            "comment": "Invalid request",
        }

        with pytest.raises(Mt5TradingError, match=r"order_send\(\) failed and aborted"):
            client._send_or_check_order(  # type: ignore[reportPrivateUsage]
                request,
                raise_on_error=True,
            )

    def test_send_or_check_order_dry_run_failure(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test _send_or_check_order in dry run mode with failure."""
        client = create_initialized_client(mock_mt5_import)

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        mock_mt5_import.order_check.return_value.retcode = 10013
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 10013,
            "comment": "Invalid request",
        }

        with pytest.raises(
            Mt5TradingError, match=r"order_check\(\) failed and aborted"
        ):
            client._send_or_check_order(  # type: ignore[reportPrivateUsage]
                request,
                raise_on_error=True,
                dry_run=True,
            )

    def test_send_or_check_order_dry_run_override(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test _send_or_check_order with dry_run parameter override."""
        client = create_initialized_client(mock_mt5_import)

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        mock_mt5_import.order_check.return_value.retcode = 0
        mock_mt5_import.order_check.return_value._asdict.return_value = {
            "retcode": 0,
            "result": "check_success",
        }

        result = client._send_or_check_order(  # type: ignore[reportPrivateUsage]
            request,
            dry_run=True,
        )

        assert result["retcode"] == 0
        assert result["result"] == "check_success"
        mock_mt5_import.order_check.assert_called_once_with(request)
        mock_mt5_import.order_send.assert_not_called()

    def test_send_or_check_order_real_mode_override(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test _send_or_check_order with real mode override."""
        client = create_initialized_client(mock_mt5_import)

        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 1,
        }

        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009,
            "result": "send_success",
        }

        result = client._send_or_check_order(  # type: ignore[reportPrivateUsage]
            request,
            dry_run=False,
        )

        assert result["retcode"] == 10009
        assert result["result"] == "send_success"
        mock_mt5_import.order_send.assert_called_once_with(request)
        mock_mt5_import.order_check.assert_not_called()

    def test_place_market_order(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test place_market_order method."""
        client = create_initialized_client(mock_mt5_import)

        mock_mt5_import.ORDER_TYPE_BUY = 0  # type: ignore[reportAttributeAccessIssue]
        mock_mt5_import.ORDER_FILLING_IOC = 1  # type: ignore[reportAttributeAccessIssue]
        mock_mt5_import.ORDER_TIME_GTC = 0  # type: ignore[reportAttributeAccessIssue]
        mock_mt5_import.TRADE_ACTION_DEAL = 1  # type: ignore[reportAttributeAccessIssue]

        mock_mt5_import.order_send.return_value.retcode = 10009
        mock_mt5_import.order_send.return_value._asdict.return_value = {
            "retcode": 10009,
            "deal": 123456,
            "order": 789012,
        }

        result = client.place_market_order(
            symbol="EURUSD",
            volume=0.1,
            order_side="BUY",
            order_filling_mode="IOC",
            order_time_mode="GTC",
        )

        assert result["retcode"] == 10009
        assert result["deal"] == 123456
        assert result["order"] == 789012

        expected_request = {
            "action": 1,  # TRADE_ACTION_DEAL
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 0,  # ORDER_TYPE_BUY
            "type_filling": 1,  # ORDER_FILLING_IOC
            "type_time": 0,  # ORDER_TIME_GTC
        }
        mock_mt5_import.order_send.assert_called_once_with(expected_request)

    @pytest.mark.parametrize(
        ("order_side", "order_type_attr", "price_key", "expected_margin"),
        [
            ("BUY", "ORDER_TYPE_BUY", "ask", 100.5),
            ("SELL", "ORDER_TYPE_SELL", "bid", 99.8),
        ],
    )
    def test_calculate_minimum_order_margin_success(
        self,
        mock_mt5_import: ModuleType,
        order_side: Literal["BUY", "SELL"],
        order_type_attr: str,
        price_key: str,
        expected_margin: float,
    ) -> None:
        """Test successful calculation of minimum order margin."""
        client = create_initialized_client(mock_mt5_import)

        mock_mt5_import.symbol_info.return_value._asdict.return_value = {
            "volume_min": 0.01,
            "name": "EURUSD",
        }
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "ask": 1.1000,
            "bid": 1.0998,
        }
        mock_mt5_import.order_calc_margin.return_value = expected_margin

        result = client.calculate_minimum_order_margin("EURUSD", order_side)

        assert result == {"volume": 0.01, "margin": expected_margin}
        tick_info = mock_mt5_import.symbol_info_tick.return_value._asdict.return_value
        mock_mt5_import.order_calc_margin.assert_called_once_with(
            getattr(mock_mt5_import, order_type_attr),
            "EURUSD",
            0.01,
            tick_info[price_key],
        )

    def test_calculate_minimum_order_margin_no_margin(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test calculation when order_calc_margin returns zero."""
        client = create_initialized_client(mock_mt5_import)

        mock_mt5_import.symbol_info.return_value._asdict.return_value = {
            "volume_min": 0.01,
            "name": "EURUSD",
        }
        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "ask": 1.1000,
            "bid": 1.0998,
        }
        mock_mt5_import.order_calc_margin.return_value = 0.0

        result = client.calculate_minimum_order_margin("EURUSD", "BUY")

        assert result == {"volume": 0.01, "margin": 0.0}
        mock_mt5_import.order_calc_margin.assert_called_once_with(
            mock_mt5_import.ORDER_TYPE_BUY,
            "EURUSD",
            0.01,
            1.1000,
        )

    def test_fetch_latest_rates_as_df_success(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test successful fetching of rate data as DataFrame."""
        client = create_initialized_client(mock_mt5_import)

        mock_mt5_import.TIMEFRAME_M1 = 1  # type: ignore[reportAttributeAccessIssue]

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
            [(1234567890, 1.1000, 1.1010, 1.0990, 1.1005, 100, 2, 10000)],
            dtype=rates_dtype,
        )
        mock_mt5_import.copy_rates_from_pos.return_value = mock_rates_data

        result = client.fetch_latest_rates_as_df("EURUSD", granularity="M1", count=10)

        assert result is not None
        mock_mt5_import.copy_rates_from_pos.assert_called_once_with(
            "EURUSD",
            1,  # timeframe
            0,  # start_pos
            10,  # count
        )

    def test_fetch_latest_rates_as_df_invalid_granularity(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test fetching rate data with invalid granularity."""
        client = create_initialized_client(mock_mt5_import)

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
        client = create_initialized_client(mock_mt5_import)

        mock_mt5_import.symbol_info_tick.return_value._asdict.return_value = {
            "time": 1234567890,
            "ask": 1.1002,
            "bid": 1.1000,
        }
        mock_mt5_import.COPY_TICKS_ALL = 1  # type: ignore[reportAttributeAccessIssue]

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
            [(1234567890, 1.1000, 1.1002, 1.1001, 100, 1234567890000, 0, 100.0)],
            dtype=ticks_dtype,
        )
        mock_mt5_import.copy_ticks_range.return_value = mock_ticks_data

        result = client.fetch_latest_ticks_as_df("EURUSD", seconds=60)

        assert result is not None
        mock_mt5_import.symbol_info_tick.assert_called_once_with("EURUSD")

        call_args = mock_mt5_import.copy_ticks_range.call_args[0]
        assert call_args[0] == "EURUSD"
        assert call_args[3] == -1  # COPY_TICKS_ALL

        assert len(result) == 1
        assert "bid" in result.columns
        assert "ask" in result.columns
        assert "last" in result.columns
        assert "volume" in result.columns

    def test_mt5_successful_trade_retcodes_property(
        self, mock_mt5_import: ModuleType
    ) -> None:
        """Test mt5_successful_trade_retcodes property returns correct set of codes."""
        client = Mt5TradingClient(mt5=mock_mt5_import)

        retcodes = client.mt5_successful_trade_retcodes

        assert isinstance(retcodes, set)
        assert retcodes == {
            mock_mt5_import.TRADE_RETCODE_PLACED,
            mock_mt5_import.TRADE_RETCODE_DONE,
            mock_mt5_import.TRADE_RETCODE_DONE_PARTIAL,
        }

    def test_mt5_failed_trade_retcodes_property(
        self, mock_mt5_import: ModuleType
    ) -> None:
        """Test mt5_failed_trade_retcodes property returns correct set of codes."""
        client = Mt5TradingClient(mt5=mock_mt5_import)

        retcodes = client.mt5_failed_trade_retcodes

        assert isinstance(retcodes, set)
        expected_codes = {
            mock_mt5_import.TRADE_RETCODE_REQUOTE,
            mock_mt5_import.TRADE_RETCODE_REJECT,
            mock_mt5_import.TRADE_RETCODE_CANCEL,
            mock_mt5_import.TRADE_RETCODE_ERROR,
            mock_mt5_import.TRADE_RETCODE_TIMEOUT,
            mock_mt5_import.TRADE_RETCODE_INVALID,
            mock_mt5_import.TRADE_RETCODE_INVALID_VOLUME,
            mock_mt5_import.TRADE_RETCODE_INVALID_PRICE,
            mock_mt5_import.TRADE_RETCODE_INVALID_STOPS,
            mock_mt5_import.TRADE_RETCODE_TRADE_DISABLED,
            mock_mt5_import.TRADE_RETCODE_MARKET_CLOSED,
            mock_mt5_import.TRADE_RETCODE_NO_MONEY,
            mock_mt5_import.TRADE_RETCODE_PRICE_CHANGED,
            mock_mt5_import.TRADE_RETCODE_PRICE_OFF,
            mock_mt5_import.TRADE_RETCODE_INVALID_EXPIRATION,
            mock_mt5_import.TRADE_RETCODE_ORDER_CHANGED,
            mock_mt5_import.TRADE_RETCODE_TOO_MANY_REQUESTS,
            mock_mt5_import.TRADE_RETCODE_NO_CHANGES,
            mock_mt5_import.TRADE_RETCODE_SERVER_DISABLES_AT,
            mock_mt5_import.TRADE_RETCODE_CLIENT_DISABLES_AT,
            mock_mt5_import.TRADE_RETCODE_LOCKED,
            mock_mt5_import.TRADE_RETCODE_FROZEN,
            mock_mt5_import.TRADE_RETCODE_INVALID_FILL,
            mock_mt5_import.TRADE_RETCODE_CONNECTION,
            mock_mt5_import.TRADE_RETCODE_ONLY_REAL,
            mock_mt5_import.TRADE_RETCODE_LIMIT_ORDERS,
            mock_mt5_import.TRADE_RETCODE_LIMIT_VOLUME,
            mock_mt5_import.TRADE_RETCODE_INVALID_ORDER,
            mock_mt5_import.TRADE_RETCODE_POSITION_CLOSED,
            mock_mt5_import.TRADE_RETCODE_INVALID_CLOSE_VOLUME,
            mock_mt5_import.TRADE_RETCODE_CLOSE_ORDER_EXIST,
            mock_mt5_import.TRADE_RETCODE_LIMIT_POSITIONS,
            mock_mt5_import.TRADE_RETCODE_REJECT_CANCEL,
            mock_mt5_import.TRADE_RETCODE_LONG_ONLY,
            mock_mt5_import.TRADE_RETCODE_SHORT_ONLY,
            mock_mt5_import.TRADE_RETCODE_CLOSE_ONLY,
            mock_mt5_import.TRADE_RETCODE_FIFO_CLOSE,
            mock_mt5_import.TRADE_RETCODE_HEDGE_PROHIBITED,
        }
        assert retcodes == expected_codes
