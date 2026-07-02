"""Tests for MetaTrader5 client wrapper."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import pytest

from pdmt5.mt5 import Mt5Client, Mt5RuntimeError

if TYPE_CHECKING:
    from unittest.mock import Mock

    from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def mock_metatrader5_import(mocker: MockerFixture) -> Mock:
    """Mock MetaTrader5 import globally for all tests."""
    mock_mt5 = mocker.Mock()
    mock_mt5.last_error.return_value = (1001, "Test error")
    mock_mt5.RES_S_OK = 1
    mocker.patch("pdmt5.mt5.importlib.import_module", return_value=mock_mt5)
    return mock_mt5


class TestMt5Client:
    """Test cases for Mt5Client class."""

    @pytest.fixture
    def mock_mt5(self, mock_metatrader5_import: Mock) -> Mock:
        """Create a mock MetaTrader5 module."""
        return mock_metatrader5_import

    @pytest.fixture
    def client(self, mock_mt5: Mock) -> Mt5Client:  # noqa: ARG002
        """Create Mt5Client instance with mocked MT5 module."""
        return Mt5Client()

    @pytest.fixture
    def initialized_client(self, mock_mt5: Mock) -> Mt5Client:
        """Create an initialized Mt5Client instance."""
        mock_mt5.initialize.return_value = True
        client = Mt5Client()
        client.initialize()
        return client

    def test_initialization(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test client initialization."""
        assert client._is_initialized is False  # type: ignore[reportPrivateUsage]
        assert client.mt5 is mock_mt5

    def test_context_manager(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test context manager functionality."""
        mock_mt5.initialize.return_value = True

        with client as ctx_client:
            assert ctx_client is client
            assert client._is_initialized is True  # type: ignore[reportPrivateUsage]
            mock_mt5.initialize.assert_called_once()

        mock_mt5.shutdown.assert_called_once()
        assert client._is_initialized is False  # type: ignore[reportPrivateUsage]

    def test_initialize_success(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test successful initialization."""
        mock_mt5.initialize.return_value = True

        result = client.initialize()

        assert result is True
        assert client._is_initialized is True  # type: ignore[reportPrivateUsage]
        mock_mt5.initialize.assert_called_once_with()

    def test_initialize_with_parameters(
        self, client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test initialization with parameters."""
        mock_mt5.initialize.return_value = True

        result = client.initialize(
            path="/path/to/mt5.exe",
            login=12345,
            password="secret",
            server="Demo",
            timeout=60000,
        )

        assert result is True
        mock_mt5.initialize.assert_called_once_with(
            "/path/to/mt5.exe",
            login=12345,
            password="secret",
            server="Demo",
            timeout=60000,
        )

    def test_initialize_failure(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test initialization failure."""
        mock_mt5.initialize.return_value = False

        result = client.initialize()

        assert result is False
        assert client._is_initialized is False  # type: ignore[reportPrivateUsage]

    def test_shutdown(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test shutdown functionality."""
        initialized_client.shutdown()

        mock_mt5.shutdown.assert_called_once()
        assert initialized_client._is_initialized is False  # type: ignore[reportPrivateUsage]

    def test_last_error(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test last_error method."""
        mock_mt5.last_error.return_value = (1001, "Test error")
        error = client.last_error()

        assert error == (1001, "Test error")
        # last_error is called twice: once by the method, once by the decorator
        assert mock_mt5.last_error.call_count == 2

    def test_initialize_if_needed_calls_initialize(
        self, client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test _initialize_if_needed calls initialize when not initialized."""
        mock_mt5.initialize.return_value = True

        assert client._is_initialized is False  # type: ignore[reportPrivateUsage]
        client._initialize_if_needed()  # type: ignore[reportPrivateUsage]

        mock_mt5.initialize.assert_called_once()
        assert client._is_initialized is True  # type: ignore[reportPrivateUsage]

    def test_login_success(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test successful login."""
        mock_mt5.login.return_value = True

        result = initialized_client.login(
            login=12345, password="secret", server="Demo", timeout=60000
        )

        assert result is True
        mock_mt5.login.assert_called_once_with(
            12345, password="secret", server="Demo", timeout=60000
        )

    def test_login_failure(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test login failure."""
        mock_mt5.login.return_value = False

        result = initialized_client.login(12345, "secret", "Demo")

        assert result is False

    @pytest.mark.parametrize(
        ("return_value", "expected"),
        [
            ((500, 3815, "01 Dec 2023"), (500, 3815, "01 Dec 2023")),
            (None, None),
        ],
        ids=["success", "failure"],
    )
    def test_version(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        return_value: tuple[int, int, str] | None,
        expected: tuple[int, int, str] | None,
    ) -> None:
        """Test version method."""
        mock_mt5.version.return_value = return_value
        result = initialized_client.version()
        assert result == expected
        mock_mt5.version.assert_called_once()

    @pytest.mark.parametrize(
        ("method_name", "return_value"),
        [
            ("symbols_total", 100),
            ("orders_total", 5),
            ("positions_total", 3),
        ],
    )
    def test_totals_methods(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        method_name: str,
        return_value: int,
    ) -> None:
        """Test simple total-returning methods."""
        getattr(mock_mt5, method_name).return_value = return_value

        result = getattr(initialized_client, method_name)()

        assert result == return_value
        getattr(mock_mt5, method_name).assert_called_once()

    def test_symbols_get(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test symbols_get method."""
        mock_symbol = mocker.MagicMock()
        mock_symbol._asdict.return_value = {"name": "EURUSD"}
        mock_mt5.symbols_get.return_value = (mock_symbol,)

        result = initialized_client.symbols_get("*USD*")

        assert result is not None
        assert len(result) == 1
        mock_mt5.symbols_get.assert_called_once_with(group="*USD*")

    def test_symbols_get_empty(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test symbols_get with empty result."""
        mock_mt5.symbols_get.return_value = None

        with pytest.raises(Mt5RuntimeError) as exc_info:
            initialized_client.symbols_get()

        assert "MT5 symbols_get returned None" in str(exc_info.value)

    @pytest.mark.parametrize("method_name", ["symbol_info", "symbol_info_tick"])
    def test_symbol_info_methods(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
        method_name: str,
    ) -> None:
        """Test symbol_info and symbol_info_tick methods."""
        mock_result = mocker.MagicMock()
        getattr(mock_mt5, method_name).return_value = mock_result

        result = getattr(initialized_client, method_name)("EURUSD")

        assert result is mock_result
        getattr(mock_mt5, method_name).assert_called_once_with("EURUSD")

    @pytest.mark.parametrize(
        "enable", [True, False], ids=["enable-true", "enable-false"]
    )
    def test_symbol_select(
        self, initialized_client: Mt5Client, mock_mt5: Mock, enable: bool
    ) -> None:
        """Test symbol_select with explicit enable flag."""
        mock_mt5.symbol_select.return_value = True

        result = initialized_client.symbol_select("EURUSD", enable)

        assert result is True
        mock_mt5.symbol_select.assert_called_once_with("EURUSD", enable)

    def test_symbol_select_default(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test symbol_select defaults to enable=True."""
        mock_mt5.symbol_select.return_value = True

        result = initialized_client.symbol_select("EURUSD")

        assert result is True
        mock_mt5.symbol_select.assert_called_once_with("EURUSD", True)  # noqa: FBT003

    @pytest.mark.parametrize("method_name", ["market_book_add", "market_book_release"])
    def test_market_book_actions(
        self, initialized_client: Mt5Client, mock_mt5: Mock, method_name: str
    ) -> None:
        """Test market_book add/release methods."""
        getattr(mock_mt5, method_name).return_value = True

        result = getattr(initialized_client, method_name)("EURUSD")

        assert result is True
        getattr(mock_mt5, method_name).assert_called_once_with("EURUSD")

    def test_market_book_get(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test market_book_get method."""
        mock_book = mocker.MagicMock()
        mock_mt5.market_book_get.return_value = (mock_book,)

        result = initialized_client.market_book_get("EURUSD")

        assert result is not None
        assert len(result) == 1
        mock_mt5.market_book_get.assert_called_once_with("EURUSD")

    @pytest.mark.parametrize(
        ("method_name", "args"),
        [
            ("copy_rates_from", ("EURUSD", 1, datetime(2023, 1, 1, tzinfo=UTC), 100)),
            ("copy_rates_from_pos", ("EURUSD", 1, 0, 100)),
            (
                "copy_rates_range",
                (
                    "EURUSD",
                    1,
                    datetime(2023, 1, 1, tzinfo=UTC),
                    datetime(2023, 1, 31, tzinfo=UTC),
                ),
            ),
            ("copy_ticks_from", ("EURUSD", datetime(2023, 1, 1, tzinfo=UTC), 1000, 0)),
            (
                "copy_ticks_range",
                (
                    "EURUSD",
                    datetime(2023, 1, 1, tzinfo=UTC),
                    datetime(2023, 1, 31, tzinfo=UTC),
                    0,
                ),
            ),
        ],
    )
    def test_copy_methods(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
        method_name: str,
        args: tuple[Any, ...],
    ) -> None:
        """Test copy_rates and copy_ticks methods."""
        mock_result = mocker.MagicMock()
        getattr(mock_mt5, method_name).return_value = mock_result

        result = getattr(initialized_client, method_name)(*args)

        assert result is mock_result
        getattr(mock_mt5, method_name).assert_called_once_with(*args)

    def test_orders_get(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test orders_get method."""
        mock_order = mocker.MagicMock()
        mock_mt5.orders_get.return_value = (mock_order,)

        result = initialized_client.orders_get(symbol="EURUSD")

        assert result is not None
        assert len(result) == 1
        mock_mt5.orders_get.assert_called_once_with(symbol="EURUSD")

    @pytest.mark.parametrize(
        ("method_name", "args", "expected"),
        [
            ("order_calc_margin", (0, "EURUSD", 1.0, 1.1234), 1000.0),
            ("order_calc_profit", (0, "EURUSD", 1.0, 1.1234, 1.1334), 100.0),
        ],
    )
    def test_calc_methods(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        method_name: str,
        args: tuple[Any, ...],
        expected: float,
    ) -> None:
        """Test order_calc_margin and order_calc_profit methods."""
        getattr(mock_mt5, method_name).return_value = expected

        result = getattr(initialized_client, method_name)(*args)

        assert result == pytest.approx(expected)
        getattr(mock_mt5, method_name).assert_called_once_with(*args)

    @pytest.mark.parametrize("method_name", ["order_check", "order_send"])
    def test_order_request_methods(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
        method_name: str,
    ) -> None:
        """Test order_check and order_send methods."""
        request = {"action": 1, "symbol": "EURUSD", "volume": 0.1}
        mock_result = mocker.MagicMock()
        getattr(mock_mt5, method_name).return_value = mock_result

        result = getattr(initialized_client, method_name)(request)

        assert result is mock_result
        getattr(mock_mt5, method_name).assert_called_once_with(request)

    def test_positions_get(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test positions_get method."""
        mock_position = mocker.MagicMock()
        mock_mt5.positions_get.return_value = (mock_position,)

        result = initialized_client.positions_get(symbol="EURUSD")

        assert result is not None
        assert len(result) == 1
        mock_mt5.positions_get.assert_called_once_with(symbol="EURUSD")

    @pytest.mark.parametrize("method_name", ["account_info", "terminal_info"])
    def test_info_methods(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
        method_name: str,
    ) -> None:
        """Test account_info and terminal_info methods."""
        mock_result = mocker.MagicMock()
        getattr(mock_mt5, method_name).return_value = mock_result

        result = getattr(initialized_client, method_name)()

        assert result is mock_result
        getattr(mock_mt5, method_name).assert_called_once()

    @pytest.mark.parametrize(
        ("method_name", "expected"),
        [
            ("history_orders_total", 10),
            ("history_deals_total", 20),
        ],
    )
    def test_history_totals(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        method_name: str,
        expected: int,
    ) -> None:
        """Test history_orders_total and history_deals_total methods."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        getattr(mock_mt5, method_name).return_value = expected

        result = getattr(initialized_client, method_name)(date_from, date_to)

        assert result == expected
        getattr(mock_mt5, method_name).assert_called_once_with(date_from, date_to)

    @pytest.mark.parametrize("method_name", ["history_orders_get", "history_deals_get"])
    def test_history_get_by_date(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
        method_name: str,
    ) -> None:
        """Test history_orders_get and history_deals_get with date range."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        mock_item = mocker.MagicMock()
        getattr(mock_mt5, method_name).return_value = (mock_item,)

        result = getattr(initialized_client, method_name)(date_from, date_to)

        assert result is not None
        assert len(result) == 1
        getattr(mock_mt5, method_name).assert_called_once_with(date_from, date_to)

    @pytest.mark.parametrize(
        ("method_name", "kwargs"),
        [
            ("history_orders_get", {"ticket": 12345}),
            ("history_orders_get", {"position": 54321}),
            ("history_deals_get", {"ticket": 12345}),
            ("history_deals_get", {"position": 54321}),
        ],
        ids=[
            "orders-by-ticket",
            "orders-by-position",
            "deals-by-ticket",
            "deals-by-position",
        ],
    )
    def test_history_get_by_id(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
        method_name: str,
        kwargs: dict[str, int],
    ) -> None:
        """Test ID filters for history_orders_get and history_deals_get."""
        mock_item = mocker.MagicMock()
        getattr(mock_mt5, method_name).return_value = (mock_item,)

        result = getattr(initialized_client, method_name)(**kwargs)

        assert result is not None
        assert len(result) == 1
        getattr(mock_mt5, method_name).assert_called_once_with(**kwargs)

    def test_history_orders_get_missing_dates(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test history_orders_get without required dates."""
        # With new implementation, calling without dates passes None, None to MT5
        mock_mt5.history_orders_get.return_value = ()
        result = initialized_client.history_orders_get()
        assert result == ()
        mock_mt5.history_orders_get.assert_called_once_with(None, None)

    @pytest.mark.parametrize(
        ("method_name", "args", "mt5_return_value"),
        [
            ("symbols_total", [], 0),
            ("orders_total", [], 0),
            ("positions_total", [], 0),
            ("symbols_get", [], None),
            ("symbol_info", ["EURUSD"], None),
            ("account_info", [], None),
            ("terminal_info", [], None),
        ],
        ids=[
            "symbols_total",
            "orders_total",
            "positions_total",
            "symbols_get",
            "symbol_info",
            "account_info",
            "terminal_info",
        ],
    )
    def test_method_not_initialized(
        self,
        client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
        method_name: str,
        args: list[Any],
        mt5_return_value: int | None,
    ) -> None:
        """Test that methods auto-initialize before delegating to the MT5 module."""
        mock_mt5.initialize.return_value = True
        safe_val = mocker.MagicMock() if mt5_return_value is None else mt5_return_value
        getattr(mock_mt5, method_name).return_value = safe_val

        getattr(client, method_name)(*args)

        mock_mt5.initialize.assert_called_once()
        getattr(mock_mt5, method_name).assert_called_once_with(*args)

    def test_error_handling_with_context(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test error handling with context information."""
        mock_mt5.symbol_info.return_value = None

        with pytest.raises(Mt5RuntimeError) as exc_info:
            initialized_client.symbol_info("EURUSD")

        error_msg = str(exc_info.value)
        assert "MT5 symbol_info returned None" in error_msg

    def test_default_mt5_import(self, mock_metatrader5_import: MockerFixture) -> None:
        """Test default MetaTrader5 module import."""
        client = Mt5Client()

        assert client.mt5 is mock_metatrader5_import

    def test_multiple_initializations(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test that multiple initializations work correctly."""
        mock_mt5.initialize.return_value = True

        # First initialization
        result1 = client.initialize()
        assert result1 is True
        assert mock_mt5.initialize.call_count == 1

        # Second initialization should call initialize again
        result2 = client.initialize()
        assert result2 is True
        assert mock_mt5.initialize.call_count == 2  # Called again

    def test_shutdown_when_not_initialized(
        self, client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test shutdown when not initialized still calls mt5.shutdown."""
        client.shutdown()

        mock_mt5.shutdown.assert_called_once()

    @pytest.mark.parametrize("method_name", ["account_info", "terminal_info"])
    def test_info_methods_raise_on_none(
        self, initialized_client: Mt5Client, mock_mt5: Mock, method_name: str
    ) -> None:
        """Test that info methods raise Mt5RuntimeError when MT5 returns None."""
        getattr(mock_mt5, method_name).return_value = None
        with pytest.raises(Mt5RuntimeError):
            getattr(initialized_client, method_name)()

    @pytest.mark.parametrize(
        "method_name", ["symbols_total", "orders_total", "positions_total"]
    )
    def test_total_methods_pass_through_none(
        self, initialized_client: Mt5Client, mock_mt5: Mock, method_name: str
    ) -> None:
        """Test that total methods pass through None without raising."""
        getattr(mock_mt5, method_name).return_value = None
        assert getattr(initialized_client, method_name)() is None

    @pytest.mark.parametrize(
        "method_name", ["history_orders_total", "history_deals_total"]
    )
    def test_history_total_methods_pass_through_none(
        self, initialized_client: Mt5Client, mock_mt5: Mock, method_name: str
    ) -> None:
        """Test that history total methods pass through None without raising."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        getattr(mock_mt5, method_name).return_value = None
        assert getattr(initialized_client, method_name)(date_from, date_to) is None

    @pytest.mark.parametrize("method_name", ["market_book_add", "market_book_release"])
    def test_market_book_add_release_pass_through_false(
        self, initialized_client: Mt5Client, mock_mt5: Mock, method_name: str
    ) -> None:
        """Test that market_book_add/release return False without raising."""
        getattr(mock_mt5, method_name).return_value = False
        assert getattr(initialized_client, method_name)("EURUSD") is False

    def test_market_book_get_raises_on_none(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test that market_book_get raises Mt5RuntimeError on None."""
        mock_mt5.market_book_get.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.market_book_get("EURUSD")

    @pytest.mark.parametrize(
        ("method_name", "args"),
        [
            ("order_calc_margin", (0, "EURUSD", 1.0, 1.1234)),
            ("order_calc_profit", (0, "EURUSD", 1.0, 1.1234, 1.1334)),
            ("order_check", ({"action": 1, "symbol": "EURUSD", "volume": 0.1},)),
            ("order_send", ({"action": 1, "symbol": "EURUSD", "volume": 0.1},)),
        ],
    )
    def test_calc_and_trading_methods_raise_on_none(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        method_name: str,
        args: tuple[Any, ...],
    ) -> None:
        """Test that calc and trading methods raise Mt5RuntimeError on None."""
        getattr(mock_mt5, method_name).return_value = None
        with pytest.raises(Mt5RuntimeError):
            getattr(initialized_client, method_name)(*args)

    @pytest.mark.parametrize(
        ("method_name", "args"),
        [
            ("copy_rates_from", ("EURUSD", 1, datetime(2023, 1, 1, tzinfo=UTC), 100)),
            ("copy_rates_from_pos", ("EURUSD", 1, 0, 100)),
            (
                "copy_rates_range",
                (
                    "EURUSD",
                    1,
                    datetime(2023, 1, 1, tzinfo=UTC),
                    datetime(2023, 1, 31, tzinfo=UTC),
                ),
            ),
            ("copy_ticks_from", ("EURUSD", datetime(2023, 1, 1, tzinfo=UTC), 1000, 0)),
            (
                "copy_ticks_range",
                (
                    "EURUSD",
                    datetime(2023, 1, 1, tzinfo=UTC),
                    datetime(2023, 1, 31, tzinfo=UTC),
                    0,
                ),
            ),
        ],
    )
    def test_copy_methods_raise_on_none(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        method_name: str,
        args: tuple[Any, ...],
    ) -> None:
        """Test that copy data methods raise Mt5RuntimeError on None."""
        getattr(mock_mt5, method_name).return_value = None
        with pytest.raises(Mt5RuntimeError):
            getattr(initialized_client, method_name)(*args)

    @pytest.mark.parametrize("method_name", ["orders_get", "positions_get"])
    def test_get_methods_empty_results(
        self, initialized_client: Mt5Client, mock_mt5: Mock, method_name: str
    ) -> None:
        """Test get methods raise on None and return empty tuple on empty result."""
        getattr(mock_mt5, method_name).return_value = None
        with pytest.raises(Mt5RuntimeError):
            getattr(initialized_client, method_name)()

        getattr(mock_mt5, method_name).return_value = ()
        result = getattr(initialized_client, method_name)()
        assert result == ()

    @pytest.mark.parametrize("method_name", ["history_orders_get", "history_deals_get"])
    def test_history_get_methods_empty_results(
        self, initialized_client: Mt5Client, mock_mt5: Mock, method_name: str
    ) -> None:
        """Test history get methods raise on None and return empty tuple otherwise."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)

        getattr(mock_mt5, method_name).return_value = None
        with pytest.raises(Mt5RuntimeError):
            getattr(initialized_client, method_name)(date_from, date_to)

        getattr(mock_mt5, method_name).return_value = ()
        result = getattr(initialized_client, method_name)(date_from, date_to)
        assert result == ()

    def test_symbol_select_failure(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test symbol_select failure."""
        mock_mt5.symbol_select.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.symbol_select("EURUSD")

    @pytest.mark.parametrize("method_name", ["history_orders_get", "history_deals_get"])
    def test_history_get_with_group(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
        method_name: str,
    ) -> None:
        """Test history_orders_get and history_deals_get with group parameter."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        mock_item = mocker.MagicMock()
        getattr(mock_mt5, method_name).return_value = (mock_item,)

        result = getattr(initialized_client, method_name)(
            date_from, date_to, group="*USD*"
        )

        assert result is not None
        assert len(result) == 1
        getattr(mock_mt5, method_name).assert_called_once_with(
            date_from, date_to, group="*USD*"
        )

    @pytest.mark.parametrize(
        ("method_name", "kwargs"),
        [
            pytest.param("orders_get", {"group": "*USD*"}, id="orders-group"),
            pytest.param("orders_get", {"ticket": 12345}, id="orders-ticket"),
            pytest.param("positions_get", {"group": "*USD*"}, id="positions-group"),
            pytest.param("positions_get", {"ticket": 12345}, id="positions-ticket"),
        ],
    )
    def test_get_methods_with_parameters(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
        method_name: str,
        kwargs: dict[str, Any],
    ) -> None:
        """Test orders_get and positions_get with method_name x kwargs cases."""
        mock_item = mocker.MagicMock()
        getattr(mock_mt5, method_name).return_value = (mock_item,)

        result = getattr(initialized_client, method_name)(**kwargs)
        assert result is not None
        getattr(mock_mt5, method_name).assert_called_with(**kwargs)

    def test_login_without_timeout(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test login method without timeout parameter."""
        mock_mt5.login.return_value = True

        result = initialized_client.login(12345, "secret", "Demo")
        assert result is True
        mock_mt5.login.assert_called_with(12345, password="secret", server="Demo")

    def test_empty_market_book_get(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test market_book_get with empty result."""
        mock_mt5.market_book_get.return_value = ()

        # Empty tuple is not None, so should not raise error
        result = initialized_client.market_book_get("EURUSD")
        assert result == ()

    def test_copy_rates_from_empty_result(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test copy_rates_from with empty result."""
        mock_mt5.copy_rates_from.return_value = []

        # Empty list is not None, so should not raise error
        result = initialized_client.copy_rates_from("EURUSD", 1, datetime.now(UTC), 100)
        assert result == []
