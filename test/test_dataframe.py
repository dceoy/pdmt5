"""Tests for pdmt5.dataframe module."""

# pyright: reportPrivateUsage=false
# pyright: reportAttributeAccessIssue=false

from collections.abc import Generator
from datetime import UTC, datetime
from types import ModuleType
from typing import Any, NamedTuple

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from pdmt5.dataframe import Mt5Config, Mt5DataClient
from pdmt5.mt5 import Mt5Client, Mt5RuntimeError

# Rebuild models to ensure they are fully defined for testing
Mt5DataClient.model_rebuild()


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
    if (
        "initialize_import_error" in request.node.name
        or "test_error_handling_without_mt5" in request.node.name
    ):
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
        mock_mt5.copy_rates_from = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_ticks_from = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_rates_from_pos = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_rates_range = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_ticks_range = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbol_info_tick = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.orders_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.positions_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_deals_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_orders_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.login = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_check = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_send = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.orders_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.positions_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_orders_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_deals_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_calc_margin = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_calc_profit = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.version = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbols_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbol_select = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.market_book_add = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.market_book_release = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.market_book_get = mocker.MagicMock()  # type: ignore[attr-defined]
        yield mock_mt5


class MockAccountInfo(NamedTuple):
    """Mock account info structure."""

    login: int
    trade_mode: int
    leverage: int
    limit_orders: int
    margin_so_mode: int
    trade_allowed: bool
    trade_expert: bool
    margin_mode: int
    currency_digits: int
    fifo_close: bool
    balance: float
    credit: float
    profit: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    margin_so_call: float
    margin_so_so: float
    margin_initial: float
    margin_maintenance: float
    assets: float
    liabilities: float
    commission_blocked: float
    name: str
    server: str
    currency: str
    company: str


class MockTerminalInfo(NamedTuple):
    """Mock terminal info structure."""

    community_account: bool
    community_connection: bool
    connected: bool
    dlls_allowed: bool
    trade_allowed: bool
    tradeapi_disabled: bool
    email_enabled: bool
    ftp_enabled: bool
    notifications_enabled: bool
    mqid: bool
    build: int
    maxbars: int
    codepage: int
    ping_last: int
    community_balance: int
    retransmission: float
    company: str
    name: str
    language: int
    path: str
    data_path: str
    commondata_path: str


class MockSymbolInfo(NamedTuple):
    """Mock symbol info structure."""

    custom: bool
    chart_mode: int
    select: bool
    visible: bool
    session_deals: int
    session_buy_orders: int
    session_sell_orders: int
    volume: int
    volumehigh: int
    volumelow: int
    time: int
    digits: int
    spread: int
    spread_float: bool
    ticks_bookdepth: int
    trade_calc_mode: int
    trade_mode: int
    start_time: int
    expiration_time: int
    trade_stops_level: int
    trade_freeze_level: int
    trade_exemode: int
    swap_mode: int
    swap_rollover3days: int
    margin_hedged_use_leg: bool
    expiration_mode: int
    filling_mode: int
    order_mode: int
    order_gtc_mode: int
    option_mode: int
    option_right: int
    bid: float
    bidlow: float
    bidhigh: float
    ask: float
    asklow: float
    askhigh: float
    last: float
    lastlow: float
    lasthigh: float
    volume_real: float
    volumehigh_real: float
    volumelow_real: float
    option_strike: float
    point: float
    trade_tick_value: float
    trade_tick_value_profit: float
    trade_tick_value_loss: float
    trade_tick_size: float
    trade_contract_size: float
    trade_accrued_interest: float
    trade_face_value: float
    trade_liquidity_rate: float
    volume_min: float
    volume_max: float
    volume_step: float
    volume_limit: float
    swap_long: float
    swap_short: float
    margin_initial: float
    margin_maintenance: float
    session_volume: float
    session_turnover: float
    session_interest: float
    session_buy_orders_volume: float
    session_sell_orders_volume: float
    session_open: float
    session_close: float
    session_aw: float
    session_price_settlement: float
    session_price_limit_min: float
    session_price_limit_max: float
    margin_hedged: float
    price_change: float
    price_volatility: float
    price_theoretical: float
    price_greeks_delta: float
    price_greeks_theta: float
    price_greeks_gamma: float
    price_greeks_vega: float
    price_greeks_rho: float
    price_greeks_omega: float
    price_sensitivity: float
    basis: str
    category: str
    currency_base: str
    currency_profit: str
    currency_margin: str
    bank: str
    description: str
    exchange: str
    formula: str
    isin: str
    name: str
    page: str
    path: str


class MockTick(NamedTuple):
    """Mock tick structure."""

    time: int
    bid: float
    ask: float
    last: float
    volume: int
    time_msc: int
    flags: int
    volume_real: float


class MockRate(NamedTuple):
    """Mock rate structure."""

    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: int
    spread: int
    real_volume: int


class MockOrder(NamedTuple):
    """Mock order structure."""

    ticket: int
    time_setup: int
    time_setup_msc: int
    time_done: int
    time_done_msc: int
    time_expiration: int
    type: int
    type_time: int
    type_filling: int
    state: int
    magic: int
    position_id: int
    position_by_id: int
    reason: int
    volume_initial: float
    volume_current: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    price_stoplimit: float
    symbol: str
    comment: str
    external_id: str


class MockPosition(NamedTuple):
    """Mock position structure."""

    ticket: int
    time: int
    time_msc: int
    time_update: int
    time_update_msc: int
    type: int
    magic: int
    identifier: int
    reason: int
    volume: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    swap: float
    profit: float
    symbol: str
    comment: str
    external_id: str


class MockDeal(NamedTuple):
    """Mock deal structure."""

    ticket: int
    order: int
    time: int
    time_msc: int
    type: int
    entry: int
    magic: int
    position_id: int
    reason: int
    volume: float
    price: float
    commission: float
    swap: float
    profit: float
    fee: float
    symbol: str
    comment: str
    external_id: str


class MockOrderCheckResult(NamedTuple):
    """Mock order check result structure."""

    retcode: int
    balance: float
    equity: float
    profit: float
    margin: float
    margin_free: float
    margin_level: float
    comment: str
    request_id: int


class MockOrderSendResult(NamedTuple):
    """Mock order send result structure."""

    retcode: int
    deal: int
    order: int
    volume: float
    price: float
    bid: float
    ask: float
    comment: str
    request_id: int


class MockBookInfo(NamedTuple):
    """Mock book info structure."""

    type: int
    price: float
    volume: float
    volume_real: float


class TestMt5Config:
    """Test Mt5Config class."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = Mt5Config()  # pyright: ignore[reportCallIssue]
        assert config.path is None
        assert config.login is None
        assert config.password is None
        assert config.server is None
        assert config.timeout is None
        assert config.portable is None

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = Mt5Config(
            login=123456,
            password="secret",
            server="Demo-Server",
            timeout=30000,
            portable=True,
        )
        assert config.login == 123456
        assert config.password == "secret"  # noqa: S105
        assert config.server == "Demo-Server"
        assert config.timeout == 30000
        assert config.portable is True

    def test_config_immutable(self) -> None:
        """Test that config is immutable."""
        config = Mt5Config()  # pyright: ignore[reportCallIssue]
        with pytest.raises(ValidationError):
            config.login = 123456


class TestMt5DataClient:
    """Test Mt5DataClient class."""

    def test_init_default(self, mock_mt5_import: ModuleType | None) -> None:
        """Test client initialization with default config."""
        assert mock_mt5_import is not None
        client = Mt5DataClient(mt5=mock_mt5_import)
        assert client.config is not None
        assert client.config.timeout is None
        assert not client._is_initialized

    def test_init_custom_config(self, mock_mt5_import: ModuleType | None) -> None:
        """Test client initialization with custom config."""
        assert mock_mt5_import is not None
        config = Mt5Config(
            login=123456,
            password="test",
            server="test-server",
            timeout=30000,
        )
        client = Mt5DataClient(mt5=mock_mt5_import, config=config)
        assert client.config == config
        assert client.config.login == 123456
        assert client.config.timeout == 30000

    def test_mt5_module_default_factory(self, mocker: MockerFixture) -> None:
        """Test initialization with default mt5 module factory."""
        # Mock the importlib.import_module to verify it's called
        mock_import = mocker.patch("importlib.import_module")
        mock_import.return_value = mocker.MagicMock()

        client = Mt5DataClient()  # pyright: ignore[reportCallIssue]

        # Verify that importlib.import_module was called with "MetaTrader5"
        mock_import.assert_called_once_with("MetaTrader5")
        assert client.mt5 == mock_import.return_value

    def test_initialize_success(self, mock_mt5_import: ModuleType | None) -> None:
        """Test successful initialization."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        result = client.initialize()

        assert result is True
        assert client._is_initialized is True
        mock_mt5_import.initialize.assert_called_once()

    def test_initialize_failure(self, mock_mt5_import: ModuleType | None) -> None:
        """Test initialization failure."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = False
        mock_mt5_import.last_error.return_value = (1, "Connection failed")

        client = Mt5DataClient(mt5=mock_mt5_import, retry_count=0)
        pattern = (
            r"MetaTrader5 initialization failed after 0 retries: "
            r"\(1, 'Connection failed'\)"
        )
        with pytest.raises(Mt5RuntimeError, match=pattern):
            client.initialize_mt5()

    def test_initialize_already_initialized(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test initialize when already initialized."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        # Set _is_initialized to True to test the early return path (line 100)
        client._is_initialized = True

        # Call initialize when already initialized - should return True immediately
        result = client.initialize()

        assert result is True  # Method returns True when already initialized
        mock_mt5_import.initialize.assert_not_called()

    def test_shutdown(self, mock_mt5_import: ModuleType | None) -> None:
        """Test shutdown."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        client.shutdown()

        assert client._is_initialized is False
        mock_mt5_import.shutdown.assert_called_once()

    def test_context_manager(self, mock_mt5_import: ModuleType | None) -> None:
        """Test context manager functionality."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        with Mt5DataClient(mt5=mock_mt5_import) as client:
            assert client._is_initialized is True
            mock_mt5_import.initialize.assert_called_once()

        mock_mt5_import.shutdown.assert_called_once()

    def test_orders_get_empty(self, mock_mt5_import: ModuleType | None) -> None:
        """Test orders_get method with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_get.return_value = []

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        orders_df = client.orders_get_as_df()
        assert orders_df.empty
        assert isinstance(orders_df, pd.DataFrame)

    def test_positions_get_empty(self, mock_mt5_import: ModuleType | None) -> None:
        """Test positions_get method with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_get.return_value = []

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        positions_df = client.positions_get_as_df()
        assert positions_df.empty
        assert isinstance(positions_df, pd.DataFrame)

    def test_error_handling_without_mt5(self) -> None:
        """Test error handling when an invalid mt5 module is provided."""
        # Test with an invalid mt5 module object
        invalid_mt5 = object()  # Not a proper module
        with pytest.raises(ValidationError):
            Mt5DataClient(mt5=invalid_mt5)  # type: ignore[arg-type]

    def test_ensure_initialized_calls_initialize(
        self,
        mock_mt5_import: ModuleType | None,
    ) -> None:
        """Test that _ensure_initialized calls initialize if not initialized."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.account_info.return_value = MockAccountInfo(
            login=123456,
            trade_mode=0,
            leverage=100,
            limit_orders=200,
            margin_so_mode=0,
            trade_allowed=True,
            trade_expert=True,
            margin_mode=0,
            currency_digits=2,
            fifo_close=False,
            balance=10000.0,
            credit=0.0,
            profit=100.0,
            equity=10100.0,
            margin=500.0,
            margin_free=9600.0,
            margin_level=2020.0,
            margin_so_call=50.0,
            margin_so_so=25.0,
            margin_initial=0.0,
            margin_maintenance=0.0,
            assets=0.0,
            liabilities=0.0,
            commission_blocked=0.0,
            name="Demo Account",
            server="Demo-Server",
            currency="USD",
            company="Test Company",
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        # Initialize the client first
        client.initialize()
        df_result = client.account_info_as_df()

        assert client._is_initialized is True
        mock_mt5_import.initialize.assert_called_once()
        assert isinstance(df_result, pd.DataFrame)

    def test_orders_get_with_data(self, mock_mt5_import: ModuleType | None) -> None:
        """Test orders_get method with data."""
        assert mock_mt5_import is not None
        mock_orders = [
            MockOrder(
                ticket=123456,
                time_setup=1640995200,
                time_setup_msc=1640995200000,
                time_done=0,
                time_done_msc=0,
                time_expiration=0,
                type=0,
                type_time=0,
                type_filling=0,
                state=1,
                magic=0,
                position_id=0,
                position_by_id=0,
                reason=0,
                volume_initial=0.1,
                volume_current=0.1,
                price_open=1.1300,
                sl=1.1200,
                tp=1.1400,
                price_current=1.1301,
                price_stoplimit=0.0,
                symbol="EURUSD",
                comment="",
                external_id="",
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_get.return_value = mock_orders

        client.initialize()
        df_result = client.orders_get_as_df(symbol="EURUSD")

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.index[0] == 123456
        assert df_result.iloc[0]["symbol"] == "EURUSD"
        assert df_result.iloc[0]["volume_initial"] == 0.1
        assert isinstance(df_result.iloc[0]["time_setup"], pd.Timestamp)

    def test_positions_get_with_data(self, mock_mt5_import: ModuleType | None) -> None:
        """Test positions_get method with data."""
        assert mock_mt5_import is not None
        mock_positions = [
            MockPosition(
                ticket=123456,
                time=1640995200,
                time_msc=1640995200000,
                time_update=1640995200,
                time_update_msc=1640995200000,
                type=0,
                magic=0,
                identifier=123456,
                reason=0,
                volume=0.1,
                price_open=1.1300,
                sl=1.1200,
                tp=1.1400,
                price_current=1.1301,
                swap=-0.5,
                profit=1.0,
                symbol="EURUSD",
                comment="",
                external_id="",
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_get.return_value = mock_positions

        client.initialize()
        df_result = client.positions_get_as_df(symbol="EURUSD")

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.index[0] == 123456
        assert df_result.iloc[0]["symbol"] == "EURUSD"
        assert df_result.iloc[0]["volume"] == 0.1
        assert isinstance(df_result.iloc[0]["time"], pd.Timestamp)
        assert isinstance(df_result.iloc[0]["time_msc"], pd.Timestamp)

    def test_login_success(self, mock_mt5_import: ModuleType | None) -> None:
        """Test login method success."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.login(123456, "password", "server.com")

        assert result is True
        mock_mt5_import.login.assert_called_once_with(
            123456,
            password="password",
            server="server.com",
        )

    def test_login_with_timeout(self, mock_mt5_import: ModuleType | None) -> None:
        """Test login method with timeout."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.login(123456, "password", "server.com", timeout=30000)

        assert result is True
        mock_mt5_import.login.assert_called_once_with(
            123456,
            password="password",
            server="server.com",
            timeout=30000,
        )

    def test_login_failure(self, mock_mt5_import: ModuleType | None) -> None:
        """Test login method failure."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.return_value = False

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.login(123456, "password", "server.com")

        assert result is False

    def test_orders_total(self, mock_mt5_import: ModuleType | None) -> None:
        """Test orders_total method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_total.return_value = 5

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.orders_total()

        assert result == 5

    def test_orders_total_none_result(self, mock_mt5_import: ModuleType | None) -> None:
        """Test orders_total method with None result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_total.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.orders_total()

        assert result is None

    def test_positions_total(self, mock_mt5_import: ModuleType | None) -> None:
        """Test positions_total method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_total.return_value = 3

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.positions_total()

        assert result == 3

    def test_positions_total_none_result(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test positions_total method with None result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_total.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.positions_total()

        assert result is None

    def test_history_orders_total(self, mock_mt5_import: ModuleType | None) -> None:
        """Test history_orders_total method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_total.return_value = 10

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.history_orders_total(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )

        assert result == 10

    def test_history_orders_total_invalid_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_total method with invalid dates."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_total.return_value = 0

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        # Method doesn't validate dates, just passes them to MT5
        result = client.history_orders_total(
            datetime(2022, 1, 2, tzinfo=UTC),
            datetime(2022, 1, 1, tzinfo=UTC),
        )
        assert result == 0

    def test_history_orders_total_none_result(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_total method with None result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_total.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.history_orders_total(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )

        assert result is None

    def test_history_deals_total(self, mock_mt5_import: ModuleType | None) -> None:
        """Test history_deals_total method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_total.return_value = 15

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.history_deals_total(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )

        assert result == 15

    def test_history_deals_total_invalid_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_total method with invalid dates."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_total.return_value = 0

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        # Method doesn't validate dates, just passes them to MT5
        result = client.history_deals_total(
            datetime(2022, 1, 2, tzinfo=UTC),
            datetime(2022, 1, 1, tzinfo=UTC),
        )
        assert result == 0

    def test_history_deals_total_none_result(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_total method with None result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_total.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.history_deals_total(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )

        assert result is None

    def test_order_calc_margin(self, mock_mt5_import: ModuleType | None) -> None:
        """Test order_calc_margin method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_margin.return_value = 100.0

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.order_calc_margin(0, "EURUSD", 0.1, 1.1300)

        assert result == 100.0

    def test_order_calc_margin_invalid_volume(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test order_calc_margin method with invalid volume."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_margin.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Invalid volume")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"order_calc_margin failed: 1 - Invalid volume"
        ):
            client.order_calc_margin(0, "EURUSD", 0.0, 1.1300)

    def test_order_calc_margin_invalid_price(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test order_calc_margin method with invalid price."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_margin.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Invalid price")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"order_calc_margin failed: 1 - Invalid price"
        ):
            client.order_calc_margin(0, "EURUSD", 0.1, 0.0)

    def test_order_calc_margin_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test order_calc_margin method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_margin.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Order calc margin failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"order_calc_margin failed: 1 - Order calc margin failed",
        ):
            client.order_calc_margin(0, "EURUSD", 0.1, 1.1300)

    def test_order_calc_profit(self, mock_mt5_import: ModuleType | None) -> None:
        """Test order_calc_profit method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_profit.return_value = 10.0

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.order_calc_profit(0, "EURUSD", 0.1, 1.1300, 1.1400)

        assert result == 10.0

    def test_order_calc_profit_invalid_volume(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test order_calc_profit method with invalid volume."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_profit.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Invalid volume")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"order_calc_profit failed: 1 - Invalid volume"
        ):
            client.order_calc_profit(0, "EURUSD", 0.0, 1.1300, 1.1400)

    def test_order_calc_profit_invalid_price_open(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test order_calc_profit method with invalid open price."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_profit.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Invalid price_open")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"order_calc_profit failed: 1 - Invalid price_open"
        ):
            client.order_calc_profit(0, "EURUSD", 0.1, 0.0, 1.1400)

    def test_order_calc_profit_invalid_price_close(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test order_calc_profit method with invalid close price."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_profit.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Invalid price_close")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"order_calc_profit failed: 1 - Invalid price_close"
        ):
            client.order_calc_profit(0, "EURUSD", 0.1, 1.1300, 0.0)

    def test_order_calc_profit_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test order_calc_profit method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_profit.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Order calc profit failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"order_calc_profit failed: 1 - Order calc profit failed",
        ):
            client.order_calc_profit(0, "EURUSD", 0.1, 1.1300, 1.1400)

    def test_version(self, mock_mt5_import: ModuleType | None) -> None:
        """Test version method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.version.return_value = (2460, 2460, "15 Feb 2022")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.version()

        assert result == (2460, 2460, "15 Feb 2022")

    def test_version_none_result(self, mock_mt5_import: ModuleType | None) -> None:
        """Test version method with None result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.version.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.version()

        assert result is None

    def test_symbols_total(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbols_total method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbols_total.return_value = 1000

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.symbols_total()

        assert result == 1000

    def test_symbols_total_none_result(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test symbols_total method with None result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbols_total.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.symbols_total()

        assert result is None

    def test_symbol_select(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_select method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_select.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.symbol_select("EURUSD")

        assert result is True

    def test_symbol_select_disable(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_select method with disable."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_select.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.symbol_select("EURUSD", enable=False)

        assert result is True

    def test_symbol_select_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_select method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_select.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Symbol select failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"symbol_select failed: 1 - Symbol select failed"
        ):
            client.symbol_select("EURUSD")

    def test_market_book_add(self, mock_mt5_import: ModuleType | None) -> None:
        """Test market_book_add method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.market_book_add.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.market_book_add("EURUSD")

        assert result is True

    def test_market_book_add_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test market_book_add method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.market_book_add.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Market book add failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"market_book_add failed: 1 - Market book add failed"
        ):
            client.market_book_add("EURUSD")

    def test_market_book_release(self, mock_mt5_import: ModuleType | None) -> None:
        """Test market_book_release method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.market_book_release.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.market_book_release("EURUSD")

        assert result is True

    def test_market_book_release_error(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test market_book_release method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.market_book_release.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Market book release failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"market_book_release failed: 1 - Market book release failed",
        ):
            client.market_book_release("EURUSD")

    def test_history_orders_get_ticket(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get method with ticket filter."""
        assert mock_mt5_import is not None
        mock_orders = [
            MockOrder(
                ticket=123456,
                time_setup=1640995200,
                time_setup_msc=1640995200000,
                time_done=0,
                time_done_msc=0,
                time_expiration=0,
                type=0,
                type_time=0,
                type_filling=0,
                state=1,
                magic=0,
                position_id=0,
                position_by_id=0,
                reason=0,
                volume_initial=0.1,
                volume_current=0.1,
                price_open=1.1300,
                sl=1.1200,
                tp=1.1400,
                price_current=1.1301,
                price_stoplimit=0.0,
                symbol="EURUSD",
                comment="",
                external_id="",
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = mock_orders

        client.initialize()
        df_result = client.history_orders_get_as_df(ticket=123456)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.index[0] == 123456

    def test_history_orders_get_position(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get method with position filter."""
        assert mock_mt5_import is not None
        mock_orders = [
            MockOrder(
                ticket=123456,
                time_setup=1640995200,
                time_setup_msc=1640995200000,
                time_done=0,
                time_done_msc=0,
                time_expiration=0,
                type=0,
                type_time=0,
                type_filling=0,
                state=1,
                magic=0,
                position_id=345678,
                position_by_id=0,
                reason=0,
                volume_initial=0.1,
                volume_current=0.1,
                price_open=1.1300,
                sl=1.1200,
                tp=1.1400,
                price_current=1.1301,
                price_stoplimit=0.0,
                symbol="EURUSD",
                comment="",
                external_id="",
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = mock_orders

        client.initialize()
        df_result = client.history_orders_get_as_df(position=345678)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["position_id"] == 345678

    def test_history_orders_get_no_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get method without dates when not using ticket."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = []
        mock_mt5_import.last_error.return_value = (1, "Invalid arguments")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError,
            match=(
                r"Both date_from and date_to must be provided"
                r" if not using ticket or position"
            ),
        ):
            client.history_orders_get_as_df()

    def test_history_orders_get_invalid_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get method with invalid date range."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(ValueError, match=r"Invalid date range"):
            client.history_orders_get_as_df(
                datetime(2022, 1, 2, tzinfo=UTC),
                datetime(2022, 1, 1, tzinfo=UTC),
            )

    def test_history_orders_get_with_symbol(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get method with symbol filter."""
        assert mock_mt5_import is not None
        mock_orders = [
            MockOrder(
                ticket=123456,
                time_setup=1640995200,
                time_setup_msc=1640995200000,
                time_done=0,
                time_done_msc=0,
                time_expiration=0,
                type=0,
                type_time=0,
                type_filling=0,
                state=1,
                magic=0,
                position_id=0,
                position_by_id=0,
                reason=0,
                volume_initial=0.1,
                volume_current=0.1,
                price_open=1.1300,
                sl=1.1200,
                tp=1.1400,
                price_current=1.1301,
                price_stoplimit=0.0,
                symbol="EURUSD",
                comment="",
                external_id="",
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = mock_orders

        client.initialize()
        df_result = client.history_orders_get_as_df(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
            symbol="EURUSD",
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["symbol"] == "EURUSD"

    def test_history_orders_get_with_group(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get method with group filter."""
        assert mock_mt5_import is not None
        mock_orders = [
            MockOrder(
                ticket=123456,
                time_setup=1640995200,
                time_setup_msc=1640995200000,
                time_done=0,
                time_done_msc=0,
                time_expiration=0,
                type=0,
                type_time=0,
                type_filling=0,
                state=1,
                magic=0,
                position_id=0,
                position_by_id=0,
                reason=0,
                volume_initial=0.1,
                volume_current=0.1,
                price_open=1.1300,
                sl=1.1200,
                tp=1.1400,
                price_current=1.1301,
                price_stoplimit=0.0,
                symbol="EURUSD",
                comment="",
                external_id="",
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = mock_orders

        client.initialize()
        df_result = client.history_orders_get_as_df(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
            group="*USD*",
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["symbol"] == "EURUSD"

    def test_history_orders_get_empty(self, mock_mt5_import: ModuleType | None) -> None:
        """Test history_orders_get method with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = []

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        orders_df = client.history_orders_get_as_df(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )
        assert orders_df.empty
        assert isinstance(orders_df, pd.DataFrame)

    def test_history_deals_get_no_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_get method without dates when not using ticket."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_get.return_value = []
        mock_mt5_import.last_error.return_value = (1, "Invalid arguments")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError,
            match=(
                r"Both date_from and date_to must be provided"
                r" if not using ticket or position"
            ),
        ):
            client.history_deals_get_as_df()

    def test_market_book_get(self, mock_mt5_import: ModuleType | None) -> None:
        """Test market_book_get method."""
        assert mock_mt5_import is not None
        mock_book = [
            MockBookInfo(
                type=0,
                price=1.1300,
                volume=100.0,
                volume_real=100.0,
            ),
            MockBookInfo(
                type=1,
                price=1.1302,
                volume=200.0,
                volume_real=200.0,
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.market_book_get.return_value = tuple(mock_book)

        client.initialize()
        result = client.market_book_get("EURUSD")

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0].type == 0
        assert result[0].price == 1.1300
        assert result[1].type == 1
        assert result[1].price == 1.1302

    def test_market_book_get_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test market_book_get method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.market_book_get.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Market book get failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"market_book_get failed: 1 - Market book get failed"
        ):
            client.market_book_get("EURUSD")

    def test_shutdown_when_not_initialized(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test shutdown method when already not initialized."""
        assert mock_mt5_import is not None

        client = Mt5DataClient(mt5=mock_mt5_import)
        # Don't initialize
        client.shutdown()  # Should not call mt5.shutdown()

        mock_mt5_import.shutdown.assert_not_called()

    def test_orders_get_missing_time_columns(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test orders_get when some time columns are missing."""
        assert mock_mt5_import is not None
        # Create mock orders data as dict without time_expiration

        class MockOrderNoTimeExpiration:
            def _asdict(self) -> dict[str, Any]:
                return {
                    "ticket": 123456,
                    "time_setup": 1640995200,
                    "time_setup_msc": 1640995200000,
                    "time_done": 0,
                    "time_done_msc": 0,
                    "type": 0,
                    "type_time": 0,
                    "type_filling": 0,
                    "state": 1,
                    "magic": 0,
                    "position_id": 0,
                    "position_by_id": 0,
                    "reason": 0,
                    "volume_initial": 0.1,
                    "volume_current": 0.1,
                    "price_open": 1.1300,
                    "sl": 1.1200,
                    "tp": 1.1400,
                    "price_current": 1.1301,
                    "price_stoplimit": 0.0,
                    "symbol": "EURUSD",
                    "comment": "",
                    "external_id": "",
                }

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_get.return_value = [MockOrderNoTimeExpiration()]

        client.initialize()
        df_result = client.orders_get_as_df()

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert "time_expiration" not in df_result.columns

    def test_positions_get_missing_time_columns(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test positions_get when some time columns are missing."""
        assert mock_mt5_import is not None
        # Create mock positions data as dict without time_update

        class MockPositionNoTimeUpdate:
            def _asdict(self) -> dict[str, Any]:
                return {
                    "ticket": 123456,
                    "time": 1640995200,
                    "time_msc": 1640995200000,
                    "time_update_msc": 1640995200000,
                    "type": 0,
                    "magic": 0,
                    "identifier": 123456,
                    "reason": 0,
                    "volume": 0.1,
                    "price_open": 1.1300,
                    "sl": 1.1200,
                    "tp": 1.1400,
                    "price_current": 1.1301,
                    "swap": 0.0,
                    "profit": 10.0,
                    "symbol": "EURUSD",
                    "comment": "",
                    "external_id": "",
                }

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_get.return_value = [MockPositionNoTimeUpdate()]

        client.initialize()
        df_result = client.positions_get_as_df()

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert "time_update" not in df_result.columns

    def test_history_orders_get_missing_time_columns(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get when some time columns are missing."""
        assert mock_mt5_import is not None
        # Create mock orders data as dict without time_done

        class MockOrderNoTimeDone:
            def _asdict(self) -> dict[str, Any]:
                return {
                    "ticket": 123456,
                    "time_setup": 1640995200,
                    "time_setup_msc": 1640995200000,
                    "time_done_msc": 0,
                    "time_expiration": 0,
                    "type": 0,
                    "type_time": 0,
                    "type_filling": 0,
                    "state": 1,
                    "magic": 0,
                    "position_id": 0,
                    "position_by_id": 0,
                    "reason": 0,
                    "volume_initial": 0.1,
                    "volume_current": 0.1,
                    "price_open": 1.1300,
                    "sl": 1.1200,
                    "tp": 1.1400,
                    "price_current": 1.1301,
                    "price_stoplimit": 0.0,
                    "symbol": "EURUSD",
                    "comment": "",
                    "external_id": "",
                }

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = [MockOrderNoTimeDone()]

        client.initialize()
        df_result = client.history_orders_get_as_df(
            datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 2, tzinfo=UTC)
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert "time_done" not in df_result.columns


class TestMt5DataClientValidation:
    """Test Mt5DataClient validation methods."""

    def test_validate_positive_count_valid(self) -> None:
        """Test _validate_positive_count with valid count."""
        # Should not raise for positive count
        Mt5DataClient._validate_positive_count(count=1)
        Mt5DataClient._validate_positive_count(count=100)

    def test_validate_positive_count_invalid(self) -> None:
        """Test _validate_positive_count with invalid count."""
        with pytest.raises(
            ValueError, match=r"Invalid count: 0\. Count must be positive\."
        ):
            Mt5DataClient._validate_positive_count(count=0)

        with pytest.raises(
            ValueError, match=r"Invalid count: -1\. Count must be positive\."
        ):
            Mt5DataClient._validate_positive_count(count=-1)

    def test_validate_date_range_valid(self) -> None:
        """Test _validate_date_range with valid date range."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 2, tzinfo=UTC)
        # Should not raise for valid date range
        Mt5DataClient._validate_date_range(date_from=date_from, date_to=date_to)

    def test_validate_date_range_invalid(self) -> None:
        """Test _validate_date_range with invalid date range."""
        date_from = datetime(2023, 1, 2, tzinfo=UTC)
        date_to = datetime(2023, 1, 1, tzinfo=UTC)
        with pytest.raises(
            ValueError, match=r"Invalid date range: from=.* must be before to=.*"
        ):
            Mt5DataClient._validate_date_range(date_from=date_from, date_to=date_to)

    def test_validate_positive_value_valid(self) -> None:
        """Test _validate_positive_value with valid values."""
        # Should not raise for positive values
        Mt5DataClient._validate_positive_value(value=1.0, name="volume")
        Mt5DataClient._validate_positive_value(value=0.1, name="volume")

    def test_validate_positive_value_invalid(self) -> None:
        """Test _validate_positive_value with invalid volume."""
        with pytest.raises(
            ValueError, match=r"Invalid volume: 0\. Volume must be positive\."
        ):
            Mt5DataClient._validate_positive_value(value=0, name="volume")

        with pytest.raises(
            ValueError, match=r"Invalid volume: -1\. Volume must be positive\."
        ):
            Mt5DataClient._validate_positive_value(value=-1, name="volume")

    def test_validate_positive_value_price_invalid(self) -> None:
        """Test _validate_positive_value with invalid price."""
        with pytest.raises(
            ValueError, match=r"Invalid price_open: 0\. Price must be positive\."
        ):
            Mt5DataClient._validate_positive_value(value=0, name="price_open")

        with pytest.raises(
            ValueError, match=r"Invalid price_close: -1\. Price must be positive\."
        ):
            Mt5DataClient._validate_positive_value(value=-1, name="price_close")

    def test_validate_non_negative_position_valid(self) -> None:
        """Test _validate_non_negative_position with valid position."""
        # Should not raise for non-negative position
        Mt5DataClient._validate_non_negative_position(position=0)
        Mt5DataClient._validate_non_negative_position(position=10)

    def test_validate_non_negative_position_invalid(self) -> None:
        """Test _validate_non_negative_position with invalid position."""
        with pytest.raises(
            ValueError,
            match=r"Invalid start_pos: -1\. Position must be non-negative\.",
        ):
            Mt5DataClient._validate_non_negative_position(position=-1)

    def test_order_check_as_dict(
        self,
        mock_mt5_import: ModuleType,
        mocker: MockerFixture,
    ) -> None:
        """Test order_check_as_dict method."""
        config = Mt5Config()

        # Mock order check result with nested structure
        mock_request = mocker.MagicMock()
        mock_request._asdict.return_value = {"action": 1, "symbol": "EURUSD"}

        mock_result = mocker.MagicMock()
        mock_result._asdict.return_value = {
            "retcode": 10009,
            "request": mock_request,
            "volume": 1.0,
        }

        with Mt5DataClient(mt5=mock_mt5_import, config=config) as client:
            mock_mt5_import.order_check.return_value = mock_result

            result = client.order_check_as_dict(
                request={"action": 1, "symbol": "EURUSD"}
            )

            assert result["retcode"] == 10009
            assert result["request"] == {"action": 1, "symbol": "EURUSD"}
            assert result["volume"] == 1.0

    def test_order_send_as_dict(
        self,
        mock_mt5_import: ModuleType,
        mocker: MockerFixture,
    ) -> None:
        """Test order_send_as_dict method."""
        config = Mt5Config()

        # Mock order send result with nested structure
        mock_request = mocker.MagicMock()
        mock_request._asdict.return_value = {"action": 1, "symbol": "EURUSD"}

        mock_result = mocker.MagicMock()
        mock_result._asdict.return_value = {
            "retcode": 10009,
            "request": mock_request,
            "order": 12345,
        }

        with Mt5DataClient(mt5=mock_mt5_import, config=config) as client:
            mock_mt5_import.order_send.return_value = mock_result

            result = client.order_send_as_dict(
                request={"action": 1, "symbol": "EURUSD"}
            )

            assert result["retcode"] == 10009
            assert result["request"] == {"action": 1, "symbol": "EURUSD"}
            assert result["order"] == 12345

    def test_copy_rates_from_as_df(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test copy_rates_from_as_df method to cover validation line."""
        config = Mt5Config()

        # Mock rates data
        rate_dtype = np.dtype([
            ("time", "int64"),
            ("open", "float64"),
            ("high", "float64"),
            ("low", "float64"),
            ("close", "float64"),
        ])
        mock_rates = np.array(
            [
                (1640995200, 1.1300, 1.1350, 1.1280, 1.1320),
            ],
            dtype=rate_dtype,
        )

        with Mt5DataClient(mt5=mock_mt5_import, config=config) as client:
            mock_mt5_import.copy_rates_from.return_value = mock_rates

            # This should trigger the _validate_positive_count call on line 163
            result = client.copy_rates_from_as_df(
                symbol="EURUSD",
                timeframe=16385,
                date_from=datetime(2023, 1, 1, tzinfo=UTC),
                count=10,
            )

            assert len(result) == 1
            assert "time" in result.index.names

    def test_copy_rates_range_as_df(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test copy_rates_range_as_df method to cover validation line."""
        config = Mt5Config()

        # Mock rates data
        rate_dtype = np.dtype([
            ("time", "int64"),
            ("open", "float64"),
            ("high", "float64"),
            ("low", "float64"),
            ("close", "float64"),
        ])
        mock_rates = np.array(
            [
                (1640995200, 1.1300, 1.1350, 1.1280, 1.1320),
            ],
            dtype=rate_dtype,
        )

        with Mt5DataClient(mt5=mock_mt5_import, config=config) as client:
            mock_mt5_import.copy_rates_range.return_value = mock_rates

            # This should trigger the _validate_date_range call on line 224
            result = client.copy_rates_range_as_df(
                symbol="EURUSD",
                timeframe=16385,
                date_from=datetime(2023, 1, 1, tzinfo=UTC),
                date_to=datetime(2023, 1, 2, tzinfo=UTC),
            )

            assert len(result) == 1
            assert "time" in result.index.names


class TestMt5DataClientRetryLogic:
    """Tests for Mt5DataClient retry logic and additional coverage."""

    def test_initialize_with_retry_logic(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test initialize method with retry logic."""
        assert mock_mt5_import is not None

        client = Mt5DataClient(mt5=mock_mt5_import, retry_count=2)

        # Mock initialize to fail first two times, succeed on third
        mock_mt5_import.initialize.side_effect = [False, False, True]
        mock_mt5_import.last_error.return_value = (1, "Test error")

        # Should succeed on third attempt
        client.initialize_mt5()

        assert mock_mt5_import.initialize.call_count == 3

    def test_initialize_with_retry_logic_warning_path(
        self, mock_mt5_import: ModuleType | None, mocker: MockerFixture
    ) -> None:
        """Test initialize method with retry logic warning path."""
        assert mock_mt5_import is not None

        client = Mt5DataClient(mt5=mock_mt5_import, retry_count=1)

        # Mock initialize to fail first time, succeed on second
        mock_mt5_import.initialize.side_effect = [False, True]
        mock_mt5_import.last_error.return_value = (1, "Test error")

        # Mock time.sleep to capture the call
        mock_sleep = mocker.patch("pdmt5.dataframe.time.sleep")

        # Should succeed on second attempt
        client.initialize_mt5()

        assert mock_mt5_import.initialize.call_count == 2
        mock_sleep.assert_called_once_with(1)

    def test_initialize_with_retry_all_failures(
        self, mock_mt5_import: ModuleType | None, mocker: MockerFixture
    ) -> None:
        """Test initialize method with retry logic when all attempts fail."""
        assert mock_mt5_import is not None

        client = Mt5DataClient(mt5=mock_mt5_import, retry_count=2)

        # Mock initialize to fail all times
        mock_mt5_import.initialize.return_value = False
        mock_mt5_import.last_error.return_value = (1, "Test error")

        # Mock time.sleep to capture the calls
        mock_sleep = mocker.patch("pdmt5.dataframe.time.sleep")

        with pytest.raises(Mt5RuntimeError) as exc_info:
            client.initialize_mt5()

        assert "MetaTrader5 initialization failed after" in str(exc_info.value)
        assert mock_mt5_import.initialize.call_count == 3  # All attempts made
        # Check that sleep was called for retries
        assert mock_sleep.call_count == 2

    def test_account_info_as_dict(self, mock_mt5_import: ModuleType | None) -> None:
        """Test account_info_as_dict method."""
        assert mock_mt5_import is not None
        mock_account = MockAccountInfo(
            login=123456,
            trade_mode=0,
            leverage=100,
            limit_orders=200,
            margin_so_mode=0,
            trade_allowed=True,
            trade_expert=True,
            margin_mode=0,
            currency_digits=2,
            fifo_close=False,
            balance=10000.0,
            credit=0.0,
            profit=100.0,
            equity=10100.0,
            margin=500.0,
            margin_free=9600.0,
            margin_level=2020.0,
            margin_so_call=50.0,
            margin_so_so=25.0,
            margin_initial=0.0,
            margin_maintenance=0.0,
            assets=0.0,
            liabilities=0.0,
            commission_blocked=0.0,
            name="Demo Account",
            server="Demo-Server",
            currency="USD",
            company="Test Company",
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.account_info.return_value = mock_account

        client.initialize()
        dict_result = client.account_info_as_dict()

        assert isinstance(dict_result, dict)
        assert dict_result["login"] == 123456
        assert dict_result["balance"] == 10000.0
        assert dict_result["currency"] == "USD"
        assert dict_result["server"] == "Demo-Server"
        assert dict_result["trade_allowed"] is True

    def test_terminal_info_as_dict(self, mock_mt5_import: ModuleType | None) -> None:
        """Test terminal_info_as_dict method."""
        assert mock_mt5_import is not None
        mock_terminal = MockTerminalInfo(
            community_account=True,
            community_connection=True,
            connected=True,
            dlls_allowed=False,
            trade_allowed=True,
            tradeapi_disabled=False,
            email_enabled=True,
            ftp_enabled=False,
            notifications_enabled=True,
            mqid=True,
            build=3815,
            maxbars=65000,
            codepage=1252,
            ping_last=50,
            community_balance=1000,
            retransmission=0.0,
            company="Test Broker",
            name="MetaTrader 5",
            language=1033,
            path="C:\\Program Files\\MetaTrader 5",
            data_path="C:\\Users\\User\\AppData\\Roaming\\MetaQuotes\\Terminal\\123",
            commondata_path="C:\\Users\\User\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common",
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.terminal_info.return_value = mock_terminal

        client.initialize()
        dict_result = client.terminal_info_as_dict()

        assert isinstance(dict_result, dict)
        assert dict_result["connected"] is True
        assert dict_result["trade_allowed"] is True
        assert dict_result["build"] == 3815
        assert dict_result["company"] == "Test Broker"
        assert dict_result["name"] == "MetaTrader 5"

    def test_symbol_info_as_dict(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_info_as_dict method."""
        assert mock_mt5_import is not None
        mock_symbol = MockSymbolInfo(
            custom=False,
            chart_mode=0,
            select=True,
            visible=True,
            session_deals=0,
            session_buy_orders=0,
            session_sell_orders=0,
            volume=0,
            volumehigh=0,
            volumelow=0,
            time=1640995200,
            digits=5,
            spread=10,
            spread_float=True,
            ticks_bookdepth=10,
            trade_calc_mode=0,
            trade_mode=4,
            start_time=0,
            expiration_time=0,
            trade_stops_level=0,
            trade_freeze_level=0,
            trade_exemode=1,
            swap_mode=1,
            swap_rollover3days=3,
            margin_hedged_use_leg=False,
            expiration_mode=7,
            filling_mode=1,
            order_mode=127,
            order_gtc_mode=0,
            option_mode=0,
            option_right=0,
            bid=1.13200,
            bidhigh=1.13500,
            bidlow=1.13000,
            ask=1.13210,
            askhigh=1.13510,
            asklow=1.13010,
            last=1.13205,
            lasthigh=1.13505,
            lastlow=1.13005,
            volume_real=1000000.0,
            volumehigh_real=2000000.0,
            volumelow_real=500000.0,
            option_strike=0.0,
            point=0.00001,
            trade_tick_value=1.0,
            trade_tick_value_profit=1.0,
            trade_tick_value_loss=1.0,
            trade_tick_size=0.00001,
            trade_contract_size=100000.0,
            trade_accrued_interest=0.0,
            trade_face_value=0.0,
            trade_liquidity_rate=0.0,
            volume_min=0.01,
            volume_max=500.0,
            volume_step=0.01,
            volume_limit=0.0,
            swap_long=-0.5,
            swap_short=-0.3,
            margin_initial=0.0,
            margin_maintenance=0.0,
            session_volume=0.0,
            session_turnover=0.0,
            session_interest=0.0,
            session_buy_orders_volume=0.0,
            session_sell_orders_volume=0.0,
            session_open=1.13100,
            session_close=1.13200,
            session_aw=0.0,
            session_price_settlement=0.0,
            session_price_limit_min=0.0,
            session_price_limit_max=0.0,
            margin_hedged=50000.0,
            price_change=0.0010,
            price_volatility=0.0,
            price_theoretical=0.0,
            price_greeks_delta=0.0,
            price_greeks_theta=0.0,
            price_greeks_gamma=0.0,
            price_greeks_vega=0.0,
            price_greeks_rho=0.0,
            price_greeks_omega=0.0,
            price_sensitivity=0.0,
            basis="",
            category="",
            currency_base="EUR",
            currency_profit="USD",
            currency_margin="USD",
            bank="",
            description="Euro vs US Dollar",
            exchange="",
            formula="",
            isin="",
            name="EURUSD",
            page="",
            path="Forex\\Majors\\EURUSD",
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_info.return_value = mock_symbol

        client.initialize()
        dict_result = client.symbol_info_as_dict("EURUSD")

        assert isinstance(dict_result, dict)
        assert dict_result["name"] == "EURUSD"
        assert dict_result["digits"] == 5
        assert dict_result["bid"] == 1.13200
        assert dict_result["ask"] == 1.13210
        assert dict_result["currency_base"] == "EUR"
        assert dict_result["currency_profit"] == "USD"

    def test_symbol_info_tick_as_dict(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_info_tick_as_dict method."""
        assert mock_mt5_import is not None
        mock_tick = MockTick(
            time=1640995200,
            bid=1.13200,
            ask=1.13210,
            last=1.13205,
            volume=100,
            time_msc=1640995200123,
            flags=134,
            volume_real=100.0,
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_info_tick.return_value = mock_tick

        client.initialize()
        dict_result = client.symbol_info_tick_as_dict("EURUSD")

        assert isinstance(dict_result, dict)
        assert dict_result["bid"] == 1.13200
        assert dict_result["ask"] == 1.13210
        assert dict_result["last"] == 1.13205
        assert dict_result["volume"] == 100
        assert dict_result["time"] == pd.Timestamp(1640995200, unit="s")
        assert dict_result["flags"] == 134

    def test_inheritance_behavior(self, mock_mt5_import: ModuleType | None) -> None:
        """Test that Mt5DataClient properly inherits from Mt5Client."""
        assert mock_mt5_import is not None
        client = Mt5DataClient(mt5=mock_mt5_import)

        assert isinstance(client, Mt5Client)

        # Test that Mt5DataClient has access to parent class methods
        assert hasattr(client, "initialize")
        assert hasattr(client, "shutdown")
        assert hasattr(client, "account_info")
        assert hasattr(client, "terminal_info")
        assert hasattr(client, "symbol_info")
        assert hasattr(client, "symbol_info_tick")
        assert hasattr(client, "copy_rates_from")
        assert hasattr(client, "copy_rates_from_pos")
        assert hasattr(client, "copy_rates_range")
        assert hasattr(client, "copy_ticks_from")
        assert hasattr(client, "copy_ticks_range")
        assert hasattr(client, "orders_get")
        assert hasattr(client, "positions_get")
        assert hasattr(client, "history_orders_get")
        assert hasattr(client, "history_deals_get")

        # Test that Mt5DataClient has its own methods
        assert hasattr(client, "account_info_as_df")
        assert hasattr(client, "terminal_info_as_df")
        assert hasattr(client, "copy_rates_from_as_df")
        assert hasattr(client, "copy_rates_from_pos_as_df")
        assert hasattr(client, "copy_rates_range_as_df")
        assert hasattr(client, "copy_ticks_from_as_df")
        assert hasattr(client, "copy_ticks_range_as_df")
        assert hasattr(client, "symbols_get_as_df")
        assert hasattr(client, "orders_get_as_df")
        assert hasattr(client, "positions_get_as_df")
        assert hasattr(client, "history_orders_get_as_df")
        assert hasattr(client, "history_deals_get_as_df")

        # Test that parent class methods work correctly
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.last_error.return_value = (0, "No error")

        result = client.initialize()
        assert result is True
        mock_mt5_import.initialize.assert_called_once()

        # Test last_error method from parent class
        error = client.last_error()
        assert error == (0, "No error")
        mock_mt5_import.last_error.assert_called_once()

    def test_validate_history_input_with_ticket(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test _validate_history_input with ticket parameter."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()

        # Should not raise when ticket is provided
        client._validate_history_input(ticket=123456)

    def test_validate_history_input_with_position(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test _validate_history_input with position parameter."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()

        # Should not raise when position is provided
        client._validate_history_input(position=789012)

    def test_validate_history_input_with_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test _validate_history_input with date parameters."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()

        # Should not raise when both dates are provided
        client._validate_history_input(
            date_from=datetime(2022, 1, 1, tzinfo=UTC),
            date_to=datetime(2022, 1, 2, tzinfo=UTC),
        )

    def test_validate_history_input_missing_date_to(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test _validate_history_input with missing date_to."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()

        # Should raise when only date_from is provided
        with pytest.raises(
            ValueError,
            match=(
                r"Both date_from and date_to must be provided"
                r" if not using ticket or position"
            ),
        ):
            client._validate_history_input(date_from=datetime(2022, 1, 1, tzinfo=UTC))

    def test_validate_history_input_missing_date_from(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test _validate_history_input with missing date_from."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()

        # Should raise when only date_to is provided
        with pytest.raises(
            ValueError,
            match=(
                r"Both date_from and date_to must be provided"
                r" if not using ticket or position"
            ),
        ):
            client._validate_history_input(date_to=datetime(2022, 1, 2, tzinfo=UTC))

    def test_validate_history_input_no_params(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test _validate_history_input with no parameters."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()

        # Should raise when no parameters are provided
        with pytest.raises(
            ValueError,
            match=(
                r"Both date_from and date_to must be provided"
                r" if not using ticket or position"
            ),
        ):
            client._validate_history_input()

    def test_history_deals_get_ticket_only(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_get method with only ticket parameter."""
        assert mock_mt5_import is not None
        mock_deals = [
            MockDeal(
                ticket=123456,
                order=789012,
                time=1640995200,
                time_msc=1640995200000,
                type=0,
                entry=0,
                magic=0,
                position_id=345678,
                reason=0,
                volume=0.1,
                price=1.1300,
                commission=-2.5,
                swap=0.0,
                profit=10.0,
                fee=0.0,
                symbol="EURUSD",
                comment="",
                external_id="",
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_get.return_value = mock_deals

        client.initialize()
        df_result = client.history_deals_get_as_df(ticket=123456)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.index[0] == 123456

    def test_history_deals_get_position_only(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_get method with only position parameter."""
        assert mock_mt5_import is not None
        mock_deals = [
            MockDeal(
                ticket=123456,
                order=789012,
                time=1640995200,
                time_msc=1640995200000,
                type=0,
                entry=0,
                magic=0,
                position_id=345678,
                reason=0,
                volume=0.1,
                price=1.1300,
                commission=-2.5,
                swap=0.0,
                profit=10.0,
                fee=0.0,
                symbol="EURUSD",
                comment="",
                external_id="",
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_get.return_value = mock_deals

        client.initialize()
        df_result = client.history_deals_get_as_df(position=345678)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["position_id"] == 345678

    def test_context_manager_with_exception(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test context manager handles exceptions properly."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        test_exception_msg = "Test exception"
        with Mt5DataClient(mt5=mock_mt5_import) as client:
            assert client._is_initialized is True
            mock_mt5_import.initialize.assert_called_once()
            with pytest.raises(ValueError, match=test_exception_msg):
                raise ValueError(test_exception_msg)

        # Shutdown should still be called even with exception
        mock_mt5_import.shutdown.assert_called_once()

    def test_initialize_already_initialized_in_context(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test initialize method when already initialized (covers line 70 exit)."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        # First initialize the client normally
        result = client.initialize()
        assert result is True
        assert client._is_initialized is True
        mock_mt5_import.initialize.assert_called_once()

        # Reset the mock
        mock_mt5_import.initialize.reset_mock()

        # Call initialize again - should take the early exit at line 70
        client.initialize()

        # Initialize should not be called since we're already initialized
        mock_mt5_import.initialize.assert_not_called()
        # The method should still return True (or whatever the expected behavior is)
        assert client._is_initialized is True
