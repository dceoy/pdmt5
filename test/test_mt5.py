"""Tests for MetaTrader5 client wrapper."""

# pyright: reportPrivateUsage=false

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

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
        assert client._is_initialized is False
        assert client.mt5 is mock_mt5

    def test_context_manager(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test context manager functionality."""
        mock_mt5.initialize.return_value = True

        with client as ctx_client:
            assert ctx_client is client
            assert client._is_initialized is True
            mock_mt5.initialize.assert_called_once()

        mock_mt5.shutdown.assert_called_once()
        assert client._is_initialized is False

    def test_initialize_success(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test successful initialization."""
        mock_mt5.initialize.return_value = True

        result = client.initialize()

        assert result is True
        assert client._is_initialized is True
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
            portable=True,
        )

        assert result is True
        mock_mt5.initialize.assert_called_once_with(
            "/path/to/mt5.exe",
            login=12345,
            password="secret",
            server="Demo",
            timeout=60000,
            portable=True,
        )

    def test_initialize_failure(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test initialization failure."""
        mock_mt5.initialize.return_value = False

        with pytest.raises(Mt5RuntimeError) as exc_info:
            client.initialize()

        assert "initialize failed" in str(exc_info.value)
        assert client._is_initialized is False

    def test_shutdown(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test shutdown functionality."""
        initialized_client.shutdown()

        mock_mt5.shutdown.assert_called_once()
        assert initialized_client._is_initialized is False

    def test_last_error(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test last_error method."""
        error = client.last_error()

        assert error == (1001, "Test error")
        mock_mt5.last_error.assert_called_once()

    def test_ensure_initialized_raises(self, client: Mt5Client) -> None:
        """Test _ensure_initialized raises when not initialized."""
        with pytest.raises(Mt5RuntimeError) as exc_info:
            client._ensure_initialized()

        assert "not initialized" in str(exc_info.value)

    def test_login_success(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test successful login."""
        mock_mt5.login.return_value = True

        result = initialized_client.login(
            login=12345, password="secret", server="Demo", timeout=60000
        )

        assert result is True
        mock_mt5.login.assert_called_once_with(
            login=12345, password="secret", server="Demo", timeout=60000
        )

    def test_login_failure(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test login failure."""
        mock_mt5.login.return_value = False

        with pytest.raises(Mt5RuntimeError) as exc_info:
            initialized_client.login(12345, "secret", "Demo")

        assert "login failed" in str(exc_info.value)

    def test_version(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test version method."""
        mock_mt5.version.return_value = (500, 3815, "01 Dec 2023")

        result = initialized_client.version()

        assert result == (500, 3815, "01 Dec 2023")
        mock_mt5.version.assert_called_once()

    def test_version_failure(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test version method failure."""
        mock_mt5.version.return_value = None

        with pytest.raises(Mt5RuntimeError) as exc_info:
            initialized_client.version()

        assert "version failed" in str(exc_info.value)

    def test_symbols_total(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test symbols_total method."""
        mock_mt5.symbols_total.return_value = 100

        result = initialized_client.symbols_total()

        assert result == 100
        mock_mt5.symbols_total.assert_called_once()

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
        mock_mt5.symbols_get.assert_called_once_with("*USD*")

    def test_symbols_get_empty(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test symbols_get with empty result."""
        mock_mt5.symbols_get.return_value = None

        with pytest.raises(Mt5RuntimeError) as exc_info:
            initialized_client.symbols_get()

        assert "symbols_get failed" in str(exc_info.value)

    def test_symbol_info(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test symbol_info method."""
        mock_info = mocker.MagicMock()
        mock_mt5.symbol_info.return_value = mock_info

        result = initialized_client.symbol_info("EURUSD")

        assert result is mock_info
        mock_mt5.symbol_info.assert_called_once_with("EURUSD")

    def test_symbol_info_tick(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test symbol_info_tick method."""
        mock_tick = mocker.MagicMock()
        mock_mt5.symbol_info_tick.return_value = mock_tick

        result = initialized_client.symbol_info_tick("EURUSD")

        assert result is mock_tick
        mock_mt5.symbol_info_tick.assert_called_once_with("EURUSD")

    def test_symbol_select(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test symbol_select method."""
        mock_mt5.symbol_select.return_value = True

        result = initialized_client.symbol_select("EURUSD", True)  # noqa: FBT003

        assert result is True
        mock_mt5.symbol_select.assert_called_once_with("EURUSD", True)  # noqa: FBT003

    def test_market_book_add(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test market_book_add method."""
        mock_mt5.market_book_add.return_value = True

        result = initialized_client.market_book_add("EURUSD")

        assert result is True
        mock_mt5.market_book_add.assert_called_once_with("EURUSD")

    def test_market_book_release(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test market_book_release method."""
        mock_mt5.market_book_release.return_value = True

        result = initialized_client.market_book_release("EURUSD")

        assert result is True
        mock_mt5.market_book_release.assert_called_once_with("EURUSD")

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

    def test_copy_rates_from(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test copy_rates_from method."""
        now = datetime.now(UTC)
        mock_rates = mocker.MagicMock()
        mock_mt5.copy_rates_from.return_value = mock_rates

        result = initialized_client.copy_rates_from("EURUSD", 1, now, 100)

        assert result is mock_rates
        mock_mt5.copy_rates_from.assert_called_once_with("EURUSD", 1, now, 100)

    def test_copy_rates_from_pos(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test copy_rates_from_pos method."""
        mock_rates = mocker.MagicMock()
        mock_mt5.copy_rates_from_pos.return_value = mock_rates

        result = initialized_client.copy_rates_from_pos("EURUSD", 1, 0, 100)

        assert result is mock_rates
        mock_mt5.copy_rates_from_pos.assert_called_once_with("EURUSD", 1, 0, 100)

    def test_copy_rates_range(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test copy_rates_range method."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        mock_rates = mocker.MagicMock()
        mock_mt5.copy_rates_range.return_value = mock_rates

        result = initialized_client.copy_rates_range("EURUSD", 1, date_from, date_to)

        assert result is mock_rates
        mock_mt5.copy_rates_range.assert_called_once_with(
            "EURUSD", 1, date_from, date_to
        )

    def test_copy_ticks_from(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test copy_ticks_from method."""
        now = datetime.now(UTC)
        mock_ticks = mocker.MagicMock()
        mock_mt5.copy_ticks_from.return_value = mock_ticks

        result = initialized_client.copy_ticks_from("EURUSD", now, 1000, 0)

        assert result is mock_ticks
        mock_mt5.copy_ticks_from.assert_called_once_with("EURUSD", now, 1000, 0)

    def test_copy_ticks_range(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test copy_ticks_range method."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        mock_ticks = mocker.MagicMock()
        mock_mt5.copy_ticks_range.return_value = mock_ticks

        result = initialized_client.copy_ticks_range("EURUSD", date_from, date_to, 0)

        assert result is mock_ticks
        mock_mt5.copy_ticks_range.assert_called_once_with(
            "EURUSD", date_from, date_to, 0
        )

    def test_orders_total(self, initialized_client: Mt5Client, mock_mt5: Mock) -> None:
        """Test orders_total method."""
        mock_mt5.orders_total.return_value = 5

        result = initialized_client.orders_total()

        assert result == 5
        mock_mt5.orders_total.assert_called_once()

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

    def test_order_calc_margin(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test order_calc_margin method."""
        mock_mt5.order_calc_margin.return_value = 1000.0

        result = initialized_client.order_calc_margin(0, "EURUSD", 1.0, 1.1234)

        assert result == 1000.0
        mock_mt5.order_calc_margin.assert_called_once_with(0, "EURUSD", 1.0, 1.1234)

    def test_order_calc_profit(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test order_calc_profit method."""
        mock_mt5.order_calc_profit.return_value = 100.0

        result = initialized_client.order_calc_profit(0, "EURUSD", 1.0, 1.1234, 1.1334)

        assert result == 100.0
        mock_mt5.order_calc_profit.assert_called_once_with(
            0, "EURUSD", 1.0, 1.1234, 1.1334
        )

    def test_order_check(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test order_check method."""
        request = {"action": 1, "symbol": "EURUSD", "volume": 0.1}
        mock_result = mocker.MagicMock()
        mock_mt5.order_check.return_value = mock_result

        result = initialized_client.order_check(request)

        assert result is mock_result
        mock_mt5.order_check.assert_called_once_with(request)

    def test_order_send(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test order_send method."""
        request = {"action": 1, "symbol": "EURUSD", "volume": 0.1}
        mock_result = mocker.MagicMock()
        mock_mt5.order_send.return_value = mock_result

        result = initialized_client.order_send(request)

        assert result is mock_result
        mock_mt5.order_send.assert_called_once_with(request)

    def test_positions_total(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test positions_total method."""
        mock_mt5.positions_total.return_value = 3

        result = initialized_client.positions_total()

        assert result == 3
        mock_mt5.positions_total.assert_called_once()

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

    def test_account_info(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test account_info method."""
        mock_info = mocker.MagicMock()
        mock_mt5.account_info.return_value = mock_info

        result = initialized_client.account_info()

        assert result is mock_info
        mock_mt5.account_info.assert_called_once()

    def test_terminal_info(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test terminal_info method."""
        mock_info = mocker.MagicMock()
        mock_mt5.terminal_info.return_value = mock_info

        result = initialized_client.terminal_info()

        assert result is mock_info
        mock_mt5.terminal_info.assert_called_once()

    def test_history_orders_total(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test history_orders_total method."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        mock_mt5.history_orders_total.return_value = 10

        result = initialized_client.history_orders_total(date_from, date_to)

        assert result == 10
        mock_mt5.history_orders_total.assert_called_once_with(date_from, date_to)

    def test_history_orders_get_by_date(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test history_orders_get with date range."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        mock_order = mocker.MagicMock()
        mock_mt5.history_orders_get.return_value = (mock_order,)

        result = initialized_client.history_orders_get(date_from, date_to)

        assert result is not None
        assert len(result) == 1
        mock_mt5.history_orders_get.assert_called_once_with(date_from, date_to)

    def test_history_orders_get_by_ticket(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test history_orders_get by ticket."""
        mock_order = mocker.MagicMock()
        mock_mt5.history_orders_get.return_value = (mock_order,)

        result = initialized_client.history_orders_get(ticket=12345)

        assert result is not None
        assert len(result) == 1
        mock_mt5.history_orders_get.assert_called_once_with(ticket=12345)

    def test_history_orders_get_missing_dates(
        self, initialized_client: Mt5Client
    ) -> None:
        """Test history_orders_get without required dates."""
        with pytest.raises(ValueError, match="date_from and date_to are required"):
            initialized_client.history_orders_get()

    def test_history_deals_total(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test history_deals_total method."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        mock_mt5.history_deals_total.return_value = 20

        result = initialized_client.history_deals_total(date_from, date_to)

        assert result == 20
        mock_mt5.history_deals_total.assert_called_once_with(date_from, date_to)

    def test_history_deals_get_by_date(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test history_deals_get with date range."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 31, tzinfo=UTC)
        mock_deal = mocker.MagicMock()
        mock_mt5.history_deals_get.return_value = (mock_deal,)

        result = initialized_client.history_deals_get(date_from, date_to)

        assert result is not None
        assert len(result) == 1
        mock_mt5.history_deals_get.assert_called_once_with(date_from, date_to)

    def test_history_deals_get_by_position(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test history_deals_get by position."""
        mock_deal = mocker.MagicMock()
        mock_mt5.history_deals_get.return_value = (mock_deal,)

        result = initialized_client.history_deals_get(position=54321)

        assert result is not None
        assert len(result) == 1
        mock_mt5.history_deals_get.assert_called_once_with(position=54321)

    def test_method_not_initialized(self, client: Mt5Client) -> None:
        """Test calling methods when not initialized."""
        methods = [
            ("symbols_total", []),
            ("symbols_get", []),
            ("symbol_info", ["EURUSD"]),
            ("account_info", []),
            ("terminal_info", []),
            ("orders_total", []),
            ("positions_total", []),
        ]

        for method_name, args in methods:
            method = getattr(client, method_name)
            with pytest.raises(Mt5RuntimeError) as exc_info:
                method(*args)
            assert "not initialized" in str(exc_info.value)

    def test_error_handling_with_context(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test error handling with context information."""
        mock_mt5.symbol_info.return_value = None

        with pytest.raises(Mt5RuntimeError) as exc_info:
            initialized_client.symbol_info("EURUSD")

        error_msg = str(exc_info.value)
        assert "symbol_info failed" in error_msg
        assert "1001 - Test error" in error_msg
        assert "symbol=EURUSD" in error_msg

    def test_default_mt5_import(self, mock_metatrader5_import: MockerFixture) -> None:
        """Test default MetaTrader5 module import."""
        client = Mt5Client()

        assert client.mt5 is mock_metatrader5_import

    def test_multiple_initializations(self, client: Mt5Client, mock_mt5: Mock) -> None:
        """Test that multiple initializations don't re-initialize."""
        mock_mt5.initialize.return_value = True

        # First initialization
        result1 = client.initialize()
        assert result1 is True
        assert mock_mt5.initialize.call_count == 1

        # Second initialization should return True without calling mt5.initialize
        result2 = client.initialize()
        assert result2 is True
        assert mock_mt5.initialize.call_count == 1  # Still 1, not called again

    def test_shutdown_when_not_initialized(
        self, client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test shutdown when not initialized doesn't call mt5.shutdown."""
        client.shutdown()

        mock_mt5.shutdown.assert_not_called()

    def test_error_handling_methods(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test error handling for methods that return None."""
        # Test methods that handle None return values
        mock_mt5.symbols_total.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.symbols_total()

        mock_mt5.orders_total.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.orders_total()

        mock_mt5.positions_total.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.positions_total()

        mock_mt5.account_info.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.account_info()

        mock_mt5.terminal_info.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.terminal_info()

        mock_mt5.history_orders_total.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.history_orders_total(
                datetime(2023, 1, 1, tzinfo=UTC),
                datetime(2023, 1, 31, tzinfo=UTC),
            )

        mock_mt5.history_deals_total.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.history_deals_total(
                datetime(2023, 1, 1, tzinfo=UTC),
                datetime(2023, 1, 31, tzinfo=UTC),
            )

    def test_market_book_failures(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test market book method failures."""
        mock_mt5.market_book_add.return_value = False
        with pytest.raises(Mt5RuntimeError):
            initialized_client.market_book_add("EURUSD")

        mock_mt5.market_book_release.return_value = False
        with pytest.raises(Mt5RuntimeError):
            initialized_client.market_book_release("EURUSD")

        mock_mt5.market_book_get.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.market_book_get("EURUSD")

    def test_calculation_methods_failures(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test calculation method failures."""
        mock_mt5.order_calc_margin.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.order_calc_margin(0, "EURUSD", 1.0, 1.1234)

        mock_mt5.order_calc_profit.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.order_calc_profit(0, "EURUSD", 1.0, 1.1234, 1.1334)

    def test_trading_methods_failures(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test trading method failures."""
        mock_mt5.order_check.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.order_check({
                "action": 1,
                "symbol": "EURUSD",
                "volume": 0.1,
            })

        mock_mt5.order_send.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.order_send({
                "action": 1,
                "symbol": "EURUSD",
                "volume": 0.1,
            })

    def test_data_methods_failures(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test data method failures."""
        mock_mt5.copy_rates_from.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.copy_rates_from("EURUSD", 1, datetime.now(UTC), 100)

        mock_mt5.copy_rates_from_pos.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.copy_rates_from_pos("EURUSD", 1, 0, 100)

        mock_mt5.copy_rates_range.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.copy_rates_range(
                "EURUSD",
                1,
                datetime(2023, 1, 1, tzinfo=UTC),
                datetime(2023, 1, 31, tzinfo=UTC),
            )

        mock_mt5.copy_ticks_from.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.copy_ticks_from("EURUSD", datetime.now(UTC), 1000, 0)

        mock_mt5.copy_ticks_range.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.copy_ticks_range(
                "EURUSD",
                datetime(2023, 1, 1, tzinfo=UTC),
                datetime(2023, 1, 31, tzinfo=UTC),
                0,
            )

    def test_orders_get_empty_results(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test orders_get with empty results."""
        mock_mt5.orders_get.return_value = None
        result = initialized_client.orders_get()
        assert result is None

        mock_mt5.orders_get.return_value = ()
        result = initialized_client.orders_get()
        assert result == ()

    def test_positions_get_empty_results(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test positions_get with empty results."""
        mock_mt5.positions_get.return_value = None
        result = initialized_client.positions_get()
        assert result is None

        mock_mt5.positions_get.return_value = ()
        result = initialized_client.positions_get()
        assert result == ()

    def test_history_methods_empty_results(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test history methods with empty results."""
        mock_mt5.history_orders_get.return_value = None
        result = initialized_client.history_orders_get(
            datetime(2023, 1, 1, tzinfo=UTC),
            datetime(2023, 1, 31, tzinfo=UTC),
        )
        assert result is None

        mock_mt5.history_orders_get.return_value = ()
        result = initialized_client.history_orders_get(
            datetime(2023, 1, 1, tzinfo=UTC),
            datetime(2023, 1, 31, tzinfo=UTC),
        )
        assert result == ()

        mock_mt5.history_deals_get.return_value = None
        result = initialized_client.history_deals_get(
            datetime(2023, 1, 1, tzinfo=UTC),
            datetime(2023, 1, 31, tzinfo=UTC),
        )
        assert result is None

        mock_mt5.history_deals_get.return_value = ()
        result = initialized_client.history_deals_get(
            datetime(2023, 1, 1, tzinfo=UTC),
            datetime(2023, 1, 31, tzinfo=UTC),
        )
        assert result == ()

    def test_symbol_select_failure(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test symbol_select failure."""
        mock_mt5.symbol_select.return_value = None
        with pytest.raises(Mt5RuntimeError):
            initialized_client.symbol_select("EURUSD")

    def test_history_orders_get_with_group(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test history_orders_get with group parameter."""
        mock_order = mocker.MagicMock()
        mock_mt5.history_orders_get.return_value = (mock_order,)

        result = initialized_client.history_orders_get(
            datetime(2023, 1, 1, tzinfo=UTC),
            datetime(2023, 1, 31, tzinfo=UTC),
            group="*USD*",
        )

        assert result is not None
        assert len(result) == 1
        mock_mt5.history_orders_get.assert_called_once_with(
            datetime(2023, 1, 1, tzinfo=UTC),
            datetime(2023, 1, 31, tzinfo=UTC),
            group="*USD*",
        )

    def test_history_deals_get_with_group(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test history_deals_get with group parameter."""
        mock_deal = mocker.MagicMock()
        mock_mt5.history_deals_get.return_value = (mock_deal,)

        result = initialized_client.history_deals_get(
            datetime(2023, 1, 1, tzinfo=UTC),
            datetime(2023, 1, 31, tzinfo=UTC),
            group="*USD*",
        )

        assert result is not None
        assert len(result) == 1
        mock_mt5.history_deals_get.assert_called_once_with(
            datetime(2023, 1, 1, tzinfo=UTC),
            datetime(2023, 1, 31, tzinfo=UTC),
            group="*USD*",
        )

    def test_orders_get_with_parameters(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test orders_get with different parameter combinations."""
        mock_order = mocker.MagicMock()
        mock_mt5.orders_get.return_value = (mock_order,)

        # Test with group parameter
        result = initialized_client.orders_get(group="*USD*")
        assert result is not None
        mock_mt5.orders_get.assert_called_with(group="*USD*")

        # Test with ticket parameter
        result = initialized_client.orders_get(ticket=12345)
        assert result is not None
        mock_mt5.orders_get.assert_called_with(ticket=12345)

    def test_positions_get_with_parameters(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test positions_get with different parameter combinations."""
        mock_position = mocker.MagicMock()
        mock_mt5.positions_get.return_value = (mock_position,)

        # Test with group parameter
        result = initialized_client.positions_get(group="*USD*")
        assert result is not None
        mock_mt5.positions_get.assert_called_with(group="*USD*")

        # Test with ticket parameter
        result = initialized_client.positions_get(ticket=12345)
        assert result is not None
        mock_mt5.positions_get.assert_called_with(ticket=12345)

    def test_symbols_get_with_empty_group(
        self,
        initialized_client: Mt5Client,
        mock_mt5: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test symbols_get with empty group parameter."""
        mock_symbol = mocker.MagicMock()
        mock_mt5.symbols_get.return_value = (mock_symbol,)

        result = initialized_client.symbols_get("")
        assert result is not None
        mock_mt5.symbols_get.assert_called_with()  # Empty string is falsy, so no args

    def test_login_without_timeout(
        self, initialized_client: Mt5Client, mock_mt5: Mock
    ) -> None:
        """Test login method without timeout parameter."""
        mock_mt5.login.return_value = True

        result = initialized_client.login(12345, "secret", "Demo")
        assert result is True
        mock_mt5.login.assert_called_with(login=12345, password="secret", server="Demo")

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
