"""Tests for pdmt5.manipulator module."""

# pyright: reportPrivateUsage=false

from collections.abc import Generator
from datetime import UTC, datetime
from types import ModuleType
from typing import Any, NamedTuple

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from pdmt5.manipulator import Mt5Config, Mt5DataClient, Mt5RuntimeError

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
    name: str
    description: str
    formula: str
    isin: str
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
        assert config.login is None
        assert config.password is None
        assert config.server is None
        assert config.timeout == 60000
        assert config.portable is False

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
        assert client.config.timeout == 60000
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

    def test_missing_mt5_module(self) -> None:
        """Test initialization without providing mt5 module."""
        with pytest.raises(ValidationError, match=r"Field required"):
            Mt5DataClient()  # pyright: ignore[reportCallIssue]

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

        client = Mt5DataClient(mt5=mock_mt5_import)
        with pytest.raises(
            Mt5RuntimeError,
            match=r"MetaTrader5 initialization failed: 1 - Connection failed",
        ):
            client.initialize()

    def test_initialize_already_initialized(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test initialize when already initialized."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()

        # Second call should return True without calling mt5.initialize again
        mock_mt5_import.initialize.reset_mock()
        result = client.initialize()

        assert result is True
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

    def test_account_info(self, mock_mt5_import: ModuleType | None) -> None:
        """Test account_info method."""
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
        df_result = client.account_info()

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["login"] == 123456
        assert df_result.iloc[0]["balance"] == 10000.0
        assert df_result.iloc[0]["currency"] == "USD"

    def test_account_info_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test account_info method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.account_info.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Account info failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"account_info failed: 1 - Account info failed",
        ):
            client.account_info()

    def test_copy_rates_from(self, mock_mt5_import: ModuleType | None) -> None:
        """Test copy_rates_from method."""
        assert mock_mt5_import is not None
        # Create structured numpy array like MetaTrader5 returns
        mock_rates = np.array(
            [
                (1640995200, 1.1300, 1.1350, 1.1250, 1.1320, 1000, 2, 0),
                (1640995260, 1.1320, 1.1380, 1.1300, 1.1360, 1200, 3, 0),
            ],
            dtype=[
                ("time", "i8"),
                ("open", "f8"),
                ("high", "f8"),
                ("low", "f8"),
                ("close", "f8"),
                ("tick_volume", "i8"),
                ("spread", "i4"),
                ("real_volume", "i8"),
            ],
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_rates_from.return_value = mock_rates

        client.initialize()
        df_result = client.copy_rates_from(
            "EURUSD", 1, datetime(2022, 1, 1, tzinfo=UTC), 2
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 2
        assert isinstance(df_result.index, pd.DatetimeIndex)
        assert df_result.iloc[0]["open"] == 1.1300
        assert df_result.iloc[0]["close"] == 1.1320
        assert df_result.iloc[1]["open"] == 1.1320
        assert df_result.iloc[1]["close"] == 1.1360

    def test_copy_ticks_from(self, mock_mt5_import: ModuleType | None) -> None:
        """Test copy_ticks_from method."""
        assert mock_mt5_import is not None
        # Create structured numpy array like MetaTrader5 returns
        mock_ticks = np.array(
            [
                (1640995200, 1.1300, 1.1302, 1.1301, 100, 1640995200000, 6, 100.0),
                (1640995201, 1.1301, 1.1303, 1.1302, 150, 1640995201000, 6, 150.0),
            ],
            dtype=[
                ("time", "i8"),
                ("bid", "f8"),
                ("ask", "f8"),
                ("last", "f8"),
                ("volume", "i8"),
                ("time_msc", "i8"),
                ("flags", "i4"),
                ("volume_real", "f8"),
            ],
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_ticks_from.return_value = mock_ticks

        client.initialize()
        df_result = client.copy_ticks_from(
            "EURUSD", datetime(2022, 1, 1, tzinfo=UTC), 2, 6
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 2
        assert isinstance(df_result.index, pd.DatetimeIndex)
        assert df_result.iloc[0]["bid"] == 1.1300
        assert df_result.iloc[0]["ask"] == 1.1302
        assert df_result.iloc[1]["bid"] == 1.1301
        assert df_result.iloc[1]["ask"] == 1.1303

    def test_symbols_get(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbols_get method."""
        assert mock_mt5_import is not None
        mock_symbols = [
            MockSymbolInfo(
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
                spread=2,
                spread_float=True,
                ticks_bookdepth=10,
                trade_calc_mode=0,
                trade_mode=4,
                start_time=0,
                expiration_time=0,
                trade_stops_level=0,
                trade_freeze_level=0,
                trade_exemode=0,
                swap_mode=1,
                swap_rollover3days=3,
                margin_hedged_use_leg=False,
                expiration_mode=15,
                filling_mode=7,
                order_mode=127,
                order_gtc_mode=0,
                option_mode=0,
                option_right=0,
                bid=1.1300,
                bidlow=1.1250,
                bidhigh=1.1350,
                ask=1.1302,
                asklow=1.1252,
                askhigh=1.1352,
                last=1.1301,
                lastlow=1.1251,
                lasthigh=1.1351,
                volume_real=0.0,
                volumehigh_real=0.0,
                volumelow_real=0.0,
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
                swap_long=-7.0,
                swap_short=2.0,
                margin_initial=0.0,
                margin_maintenance=0.0,
                session_volume=0.0,
                session_turnover=0.0,
                session_interest=0.0,
                session_buy_orders_volume=0.0,
                session_sell_orders_volume=0.0,
                session_open=1.1300,
                session_close=1.1320,
                session_aw=1.1310,
                session_price_settlement=0.0,
                session_price_limit_min=0.0,
                session_price_limit_max=0.0,
                margin_hedged=50000.0,
                price_change=0.0020,
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
                name="EURUSD",
                description="Euro vs US Dollar",
                formula="",
                isin="",
                page="",
                path="",
            ),
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbols_get.return_value = mock_symbols

        client.initialize()
        df_result = client.symbols_get()

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["name"] == "EURUSD"
        assert df_result.iloc[0]["currency_base"] == "EUR"
        assert df_result.iloc[0]["currency_profit"] == "USD"

    def test_orders_get_empty(self, mock_mt5_import: ModuleType | None) -> None:
        """Test orders_get method with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_get.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        df_result = client.orders_get()

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 0

    def test_positions_get_empty(self, mock_mt5_import: ModuleType | None) -> None:
        """Test positions_get method with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_get.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        df_result = client.positions_get()

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 0

    def test_error_handling_without_mt5(self) -> None:
        """Test error handling when MetaTrader5 module is not provided."""
        with pytest.raises(ValidationError, match=r"Field required"):
            Mt5DataClient()  # pyright: ignore[reportCallIssue]

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
        # This should call initialize automatically
        df_result = client.account_info()

        assert client._is_initialized is True
        mock_mt5_import.initialize.assert_called_once()
        assert isinstance(df_result, pd.DataFrame)

    def test_history_deals_get(self, mock_mt5_import: ModuleType | None) -> None:
        """Test history_deals_get method."""
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
                commission=-0.70,
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
        df_result = client.history_deals_get(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
            symbol="EURUSD",
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["ticket"] == 123456
        assert df_result.iloc[0]["symbol"] == "EURUSD"
        assert df_result.iloc[0]["volume"] == 0.1
        assert df_result.iloc[0]["profit"] == 10.0
        # Check that time columns are converted to datetime
        assert isinstance(df_result.iloc[0]["time"], pd.Timestamp)
        assert isinstance(df_result.iloc[0]["time_msc"], pd.Timestamp)

    def test_terminal_info(self, mock_mt5_import: ModuleType | None) -> None:
        """Test terminal_info method."""
        assert mock_mt5_import is not None
        mock_terminal = MockTerminalInfo(
            community_account=False,
            community_connection=False,
            connected=True,
            dlls_allowed=True,
            trade_allowed=True,
            tradeapi_disabled=False,
            email_enabled=False,
            ftp_enabled=False,
            notifications_enabled=False,
            mqid=False,
            build=3490,
            maxbars=100000,
            codepage=1251,
            ping_last=123,
            community_balance=0,
            retransmission=0.0,
            company="Test Company",
            name="MetaTrader 5",
            language=1033,
            data_path="/path/to/data",
            commondata_path="/path/to/common",
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.terminal_info.return_value = mock_terminal

        client.initialize()
        df_result = client.terminal_info()

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["build"] == 3490
        assert df_result.iloc[0]["connected"]
        assert df_result.iloc[0]["name"] == "MetaTrader 5"

    def test_terminal_info_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test terminal_info method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.terminal_info.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Terminal info failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"terminal_info failed: 1 - Terminal info failed",
        ):
            client.terminal_info()

    def test_copy_rates_from_pos(self, mock_mt5_import: ModuleType | None) -> None:
        """Test copy_rates_from_pos method."""
        assert mock_mt5_import is not None
        mock_rates = np.array(
            [
                (1640995200, 1.1300, 1.1350, 1.1250, 1.1320, 1000, 2, 0),
                (1640995260, 1.1320, 1.1380, 1.1300, 1.1360, 1200, 3, 0),
            ],
            dtype=[
                ("time", "i8"),
                ("open", "f8"),
                ("high", "f8"),
                ("low", "f8"),
                ("close", "f8"),
                ("tick_volume", "i8"),
                ("spread", "i4"),
                ("real_volume", "i8"),
            ],
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_rates_from_pos.return_value = mock_rates

        client.initialize()
        df_result = client.copy_rates_from_pos("EURUSD", 1, 0, 2)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 2
        assert isinstance(df_result.index, pd.DatetimeIndex)
        assert df_result.iloc[0]["open"] == 1.1300
        assert df_result.iloc[0]["close"] == 1.1320

    def test_copy_rates_from_pos_invalid_count(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test copy_rates_from_pos method with invalid count."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError, match=r"Invalid count: 0. Count must be positive."
        ):
            client.copy_rates_from_pos("EURUSD", 1, 0, 0)

    def test_copy_rates_from_pos_invalid_start_pos(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test copy_rates_from_pos method with invalid start_pos."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError, match=r"Invalid start_pos: -1. Position must be non-negative."
        ):
            client.copy_rates_from_pos("EURUSD", 1, -1, 2)

    def test_copy_rates_from_pos_error(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test copy_rates_from_pos method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_rates_from_pos.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Rates retrieval failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"copy_rates_from_pos failed: 1 - Rates retrieval failed",
        ):
            client.copy_rates_from_pos("EURUSD", 1, 0, 2)

    def test_copy_rates_range(self, mock_mt5_import: ModuleType | None) -> None:
        """Test copy_rates_range method."""
        assert mock_mt5_import is not None
        mock_rates = np.array(
            [
                (1640995200, 1.1300, 1.1350, 1.1250, 1.1320, 1000, 2, 0),
                (1640995260, 1.1320, 1.1380, 1.1300, 1.1360, 1200, 3, 0),
            ],
            dtype=[
                ("time", "i8"),
                ("open", "f8"),
                ("high", "f8"),
                ("low", "f8"),
                ("close", "f8"),
                ("tick_volume", "i8"),
                ("spread", "i4"),
                ("real_volume", "i8"),
            ],
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_rates_range.return_value = mock_rates

        client.initialize()
        df_result = client.copy_rates_range(
            "EURUSD",
            1,
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 2
        assert isinstance(df_result.index, pd.DatetimeIndex)
        assert df_result.iloc[0]["open"] == 1.1300
        assert df_result.iloc[0]["close"] == 1.1320

    def test_copy_rates_range_invalid_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test copy_rates_range method with invalid date range."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(ValueError, match=r"Invalid date range"):
            client.copy_rates_range(
                "EURUSD",
                1,
                datetime(2022, 1, 2, tzinfo=UTC),
                datetime(2022, 1, 1, tzinfo=UTC),
            )

    def test_copy_rates_range_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test copy_rates_range method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_rates_range.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Rates range retrieval failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"copy_rates_range failed: 1 - Rates range retrieval failed",
        ):
            client.copy_rates_range(
                "EURUSD",
                1,
                datetime(2022, 1, 1, tzinfo=UTC),
                datetime(2022, 1, 2, tzinfo=UTC),
            )

    def test_copy_ticks_range(self, mock_mt5_import: ModuleType | None) -> None:
        """Test copy_ticks_range method."""
        assert mock_mt5_import is not None
        mock_ticks = np.array(
            [
                (1640995200, 1.1300, 1.1302, 1.1301, 100, 1640995200000, 6, 100.0),
                (1640995201, 1.1301, 1.1303, 1.1302, 150, 1640995201000, 6, 150.0),
            ],
            dtype=[
                ("time", "i8"),
                ("bid", "f8"),
                ("ask", "f8"),
                ("last", "f8"),
                ("volume", "i8"),
                ("time_msc", "i8"),
                ("flags", "i4"),
                ("volume_real", "f8"),
            ],
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_ticks_range.return_value = mock_ticks

        client.initialize()
        df_result = client.copy_ticks_range(
            "EURUSD",
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
            6,
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 2
        assert isinstance(df_result.index, pd.DatetimeIndex)
        assert df_result.iloc[0]["bid"] == 1.1300
        assert df_result.iloc[0]["ask"] == 1.1302

    def test_copy_ticks_range_invalid_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test copy_ticks_range method with invalid date range."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(ValueError, match=r"Invalid date range"):
            client.copy_ticks_range(
                "EURUSD",
                datetime(2022, 1, 2, tzinfo=UTC),
                datetime(2022, 1, 1, tzinfo=UTC),
                6,
            )

    def test_copy_ticks_range_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test copy_ticks_range method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_ticks_range.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Ticks range retrieval failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"copy_ticks_range failed: 1 - Ticks range retrieval failed",
        ):
            client.copy_ticks_range(
                "EURUSD",
                datetime(2022, 1, 1, tzinfo=UTC),
                datetime(2022, 1, 2, tzinfo=UTC),
                6,
            )

    def test_symbol_info(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_info method."""
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
            spread=2,
            spread_float=True,
            ticks_bookdepth=10,
            trade_calc_mode=0,
            trade_mode=4,
            start_time=0,
            expiration_time=0,
            trade_stops_level=0,
            trade_freeze_level=0,
            trade_exemode=0,
            swap_mode=0,
            swap_rollover3days=0,
            margin_hedged_use_leg=False,
            expiration_mode=0,
            filling_mode=0,
            order_mode=0,
            order_gtc_mode=0,
            option_mode=0,
            option_right=0,
            bid=1.1300,
            bidlow=1.1250,
            bidhigh=1.1350,
            ask=1.1302,
            asklow=1.1252,
            askhigh=1.1352,
            last=1.1301,
            lastlow=1.1251,
            lasthigh=1.1351,
            volume_real=0.0,
            volumehigh_real=0.0,
            volumelow_real=0.0,
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
            swap_long=-2.5,
            swap_short=-0.5,
            margin_initial=0.0,
            margin_maintenance=0.0,
            session_volume=0.0,
            session_turnover=0.0,
            session_interest=0.0,
            session_buy_orders_volume=0.0,
            session_sell_orders_volume=0.0,
            session_open=1.1300,
            session_close=1.1300,
            session_aw=1.1300,
            session_price_settlement=1.1300,
            session_price_limit_min=1.1200,
            session_price_limit_max=1.1400,
            margin_hedged=50.0,
            price_change=0.0,
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
            currency_margin="EUR",
            name="EURUSD",
            description="Euro vs US Dollar",
            formula="",
            isin="",
            page="",
            path="Forex\\Major",
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_info.return_value = mock_symbol

        client.initialize()
        df_result = client.symbol_info("EURUSD")

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["name"] == "EURUSD"
        assert df_result.iloc[0]["currency_base"] == "EUR"
        assert df_result.iloc[0]["currency_profit"] == "USD"

    def test_symbol_info_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_info method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_info.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Symbol info failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"symbol_info failed: 1 - Symbol info failed",
        ):
            client.symbol_info("EURUSD")

    def test_symbol_info_tick(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_info_tick method."""
        assert mock_mt5_import is not None
        mock_tick = MockTick(
            time=1640995200,
            bid=1.1300,
            ask=1.1302,
            last=1.1301,
            volume=100,
            time_msc=1640995200000,
            flags=6,
            volume_real=100.0,
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_info_tick.return_value = mock_tick

        client.initialize()
        df_result = client.symbol_info_tick("EURUSD")

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["bid"] == 1.1300
        assert df_result.iloc[0]["ask"] == 1.1302
        assert isinstance(df_result.iloc[0]["time"], pd.Timestamp)
        assert isinstance(df_result.iloc[0]["time_msc"], pd.Timestamp)

    def test_symbol_info_tick_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_info_tick method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_info_tick.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Symbol tick failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"symbol_info_tick failed: 1 - Symbol tick failed",
        ):
            client.symbol_info_tick("EURUSD")

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
        df_result = client.orders_get(symbol="EURUSD")

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["ticket"] == 123456
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
        df_result = client.positions_get(symbol="EURUSD")

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["ticket"] == 123456
        assert df_result.iloc[0]["symbol"] == "EURUSD"
        assert df_result.iloc[0]["volume"] == 0.1
        assert isinstance(df_result.iloc[0]["time"], pd.Timestamp)
        assert isinstance(df_result.iloc[0]["time_msc"], pd.Timestamp)

    def test_copy_ticks_from_invalid_count(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test copy_ticks_from method with invalid count."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError, match=r"Invalid count: 0. Count must be positive."
        ):
            client.copy_ticks_from("EURUSD", datetime(2022, 1, 1, tzinfo=UTC), 0, 6)

    def test_copy_ticks_from_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test copy_ticks_from method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_ticks_from.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Ticks retrieval failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"copy_ticks_from failed: 1 - Ticks retrieval failed",
        ):
            client.copy_ticks_from("EURUSD", datetime(2022, 1, 1, tzinfo=UTC), 2, 6)

    def test_copy_rates_from_invalid_count(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test copy_rates_from method with invalid count."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError, match=r"Invalid count: 0. Count must be positive."
        ):
            client.copy_rates_from("EURUSD", 1, datetime(2022, 1, 1, tzinfo=UTC), 0)

    def test_copy_rates_from_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test copy_rates_from method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_rates_from.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Rates retrieval failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"copy_rates_from failed: 1 - Rates retrieval failed",
        ):
            client.copy_rates_from("EURUSD", 1, datetime(2022, 1, 1, tzinfo=UTC), 2)

    def test_symbols_get_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbols_get method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbols_get.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Symbols retrieval failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"symbols_get failed: 1 - Symbols retrieval failed",
        ):
            client.symbols_get()

    def test_history_deals_get_ticket(self, mock_mt5_import: ModuleType | None) -> None:
        """Test history_deals_get method with ticket filter."""
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
                commission=-0.70,
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
        df_result = client.history_deals_get(ticket=123456)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["ticket"] == 123456

    def test_history_deals_get_position(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_get method with position filter."""
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
                commission=-0.70,
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
        df_result = client.history_deals_get(position=345678)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["position_id"] == 345678

    def test_history_deals_get_no_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_get method without dates when not using ticket."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(ValueError, match=r"date_from and date_to are required"):
            client.history_deals_get()

    def test_history_deals_get_invalid_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_get method with invalid date range."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(ValueError, match=r"Invalid date range"):
            client.history_deals_get(
                datetime(2022, 1, 2, tzinfo=UTC),
                datetime(2022, 1, 1, tzinfo=UTC),
            )

    def test_history_deals_get_with_group(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_get method with group filter."""
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
                commission=-0.70,
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
        df_result = client.history_deals_get(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
            group="*USD*",
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["symbol"] == "EURUSD"

    def test_history_deals_get_empty(self, mock_mt5_import: ModuleType | None) -> None:
        """Test history_deals_get method with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_get.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        df_result = client.history_deals_get(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 0

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
            login=123456,
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
            login=123456,
            password="password",
            server="server.com",
            timeout=30000,
        )

    def test_login_failure(self, mock_mt5_import: ModuleType | None) -> None:
        """Test login method failure."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.return_value = False
        mock_mt5_import.last_error.return_value = (1, "Login failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(Mt5RuntimeError, match=r"login failed: 1 - Login failed"):
            client.login(123456, "password", "server.com")

    def test_orders_total(self, mock_mt5_import: ModuleType | None) -> None:
        """Test orders_total method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_total.return_value = 5

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.orders_total()

        assert result == 5

    def test_orders_total_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test orders_total method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_total.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Orders total failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"orders_total failed: 1 - Orders total failed"
        ):
            client.orders_total()

    def test_positions_total(self, mock_mt5_import: ModuleType | None) -> None:
        """Test positions_total method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_total.return_value = 3

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.positions_total()

        assert result == 3

    def test_positions_total_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test positions_total method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_total.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Positions total failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"positions_total failed: 1 - Positions total failed"
        ):
            client.positions_total()

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

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(ValueError, match=r"Invalid date range"):
            client.history_orders_total(
                datetime(2022, 1, 2, tzinfo=UTC),
                datetime(2022, 1, 1, tzinfo=UTC),
            )

    def test_history_orders_total_error(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_total method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_total.return_value = None
        mock_mt5_import.last_error.return_value = (1, "History orders total failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"history_orders_total failed: 1 - History orders total failed",
        ):
            client.history_orders_total(
                datetime(2022, 1, 1, tzinfo=UTC),
                datetime(2022, 1, 2, tzinfo=UTC),
            )

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

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(ValueError, match=r"Invalid date range"):
            client.history_deals_total(
                datetime(2022, 1, 2, tzinfo=UTC),
                datetime(2022, 1, 1, tzinfo=UTC),
            )

    def test_history_deals_total_error(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_total method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_total.return_value = None
        mock_mt5_import.last_error.return_value = (1, "History deals total failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError,
            match=r"history_deals_total failed: 1 - History deals total failed",
        ):
            client.history_deals_total(
                datetime(2022, 1, 1, tzinfo=UTC),
                datetime(2022, 1, 2, tzinfo=UTC),
            )

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

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError, match=r"Invalid volume: 0.0. Volume must be positive."
        ):
            client.order_calc_margin(0, "EURUSD", 0.0, 1.1300)

    def test_order_calc_margin_invalid_price(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test order_calc_margin method with invalid price."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError, match=r"Invalid price: 0.0. Price must be positive."
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

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError, match=r"Invalid volume: 0.0. Volume must be positive."
        ):
            client.order_calc_profit(0, "EURUSD", 0.0, 1.1300, 1.1400)

    def test_order_calc_profit_invalid_price_open(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test order_calc_profit method with invalid open price."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError, match=r"Invalid price_open: 0.0. Price must be positive."
        ):
            client.order_calc_profit(0, "EURUSD", 0.1, 0.0, 1.1400)

    def test_order_calc_profit_invalid_price_close(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test order_calc_profit method with invalid close price."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            ValueError, match=r"Invalid price_close: 0.0. Price must be positive."
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

    def test_version_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test version method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.version.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Version failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"version failed: 1 - Version failed"
        ):
            client.version()

    def test_symbols_total(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbols_total method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbols_total.return_value = 1000

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        result = client.symbols_total()

        assert result == 1000

    def test_symbols_total_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbols_total method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbols_total.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Symbols total failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5RuntimeError, match=r"symbols_total failed: 1 - Symbols total failed"
        ):
            client.symbols_total()

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
        df_result = client.history_orders_get(ticket=123456)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["ticket"] == 123456

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
        df_result = client.history_orders_get(position=345678)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["position_id"] == 345678

    def test_history_orders_get_no_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get method without dates when not using ticket."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(ValueError, match=r"date_from and date_to are required"):
            client.history_orders_get()

    def test_history_orders_get_invalid_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get method with invalid date range."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(ValueError, match=r"Invalid date range"):
            client.history_orders_get(
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
        df_result = client.history_orders_get(
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
        df_result = client.history_orders_get(
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
        mock_mt5_import.history_orders_get.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        df_result = client.history_orders_get(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 0

    def test_order_check(self, mock_mt5_import: ModuleType | None) -> None:
        """Test order_check method."""
        assert mock_mt5_import is not None
        mock_result = MockOrderCheckResult(
            retcode=10009,
            balance=10000.0,
            equity=10100.0,
            profit=100.0,
            margin=500.0,
            margin_free=9600.0,
            margin_level=2020.0,
            comment="Success",
            request_id=1,
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_check.return_value = mock_result

        client.initialize()
        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 0,
            "price": 1.1300,
        }
        df_result = client.order_check(request)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["retcode"] == 10009
        assert df_result.iloc[0]["balance"] == 10000.0

    def test_order_check_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test order_check method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_check.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Order check failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 0,
            "price": 1.1300,
        }
        with pytest.raises(
            Mt5RuntimeError, match=r"order_check failed: 1 - Order check failed"
        ):
            client.order_check(request)

    def test_order_send(self, mock_mt5_import: ModuleType | None) -> None:
        """Test order_send method."""
        assert mock_mt5_import is not None
        mock_result = MockOrderSendResult(
            retcode=10009,
            deal=12345,
            order=67890,
            volume=0.1,
            price=1.1300,
            bid=1.1298,
            ask=1.1302,
            comment="Success",
            request_id=1,
        )

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_send.return_value = mock_result

        client.initialize()
        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 0,
            "price": 1.1300,
        }
        df_result = client.order_send(request)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.iloc[0]["retcode"] == 10009
        assert df_result.iloc[0]["deal"] == 12345
        assert df_result.iloc[0]["order"] == 67890

    def test_order_send_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test order_send method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_send.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Order send failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        request = {
            "action": 1,
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": 0,
            "price": 1.1300,
        }
        with pytest.raises(
            Mt5RuntimeError, match=r"order_send failed: 1 - Order send failed"
        ):
            client.order_send(request)

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
        mock_mt5_import.market_book_get.return_value = mock_book

        client.initialize()
        df_result = client.market_book_get("EURUSD")

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 2
        assert df_result.iloc[0]["type"] == 0
        assert df_result.iloc[0]["price"] == 1.1300
        assert df_result.iloc[1]["type"] == 1
        assert df_result.iloc[1]["price"] == 1.1302

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

    def test_copy_ticks_from_without_time_msc(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test copy_ticks_from when time_msc column is not present."""
        assert mock_mt5_import is not None
        # Create mock ticks data as dict without time_msc
        mock_ticks = [
            {
                "time": 1640995200,
                "bid": 1.1300,
                "ask": 1.1301,
                "last": 1.1300,
                "volume": 100,
                "flags": 3,
                "volume_real": 100.0,
            },
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_ticks_from.return_value = mock_ticks

        client.initialize()
        df_result = client.copy_ticks_from(
            "EURUSD", datetime(2022, 1, 1, tzinfo=UTC), 10, 3
        )

        assert isinstance(df_result, pd.DataFrame)
        assert "time_msc" not in df_result.columns

    def test_copy_ticks_range_without_time_msc(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test copy_ticks_range when time_msc column is not present."""
        assert mock_mt5_import is not None
        # Create mock ticks data as dict without time_msc
        mock_ticks = [
            {
                "time": 1640995200,
                "bid": 1.1300,
                "ask": 1.1301,
                "last": 1.1300,
                "volume": 100,
                "flags": 3,
                "volume_real": 100.0,
            },
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.copy_ticks_range.return_value = mock_ticks

        client.initialize()
        df_result = client.copy_ticks_range(
            "EURUSD",
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
            3,
        )

        assert isinstance(df_result, pd.DataFrame)
        assert "time_msc" not in df_result.columns

    def test_symbol_info_tick_without_time_msc(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test symbol_info_tick when time_msc is not in tick dict."""
        assert mock_mt5_import is not None
        # Create a mock that has _asdict but doesn't include time_msc

        class MockTickNoTimeMsc:
            def _asdict(self) -> dict[str, Any]:
                return {
                    "time": 1640995200,
                    "bid": 1.1300,
                    "ask": 1.1301,
                    "last": 1.1300,
                    "volume": 100,
                    "flags": 3,
                    "volume_real": 100.0,
                }

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_info_tick.return_value = MockTickNoTimeMsc()

        client.initialize()
        df_result = client.symbol_info_tick("EURUSD")

        assert isinstance(df_result, pd.DataFrame)
        assert "time_msc" not in df_result.columns

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
        df_result = client.orders_get()

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
        df_result = client.positions_get()

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
        df_result = client.history_orders_get(
            datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 2, tzinfo=UTC)
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert "time_done" not in df_result.columns

    def test_history_deals_get_missing_time_columns(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_deals_get when some time columns are missing."""
        assert mock_mt5_import is not None
        # Create mock deals data as dict without time_msc

        class MockDealNoTimeMsc:
            def _asdict(self) -> dict[str, Any]:
                return {
                    "ticket": 123456,
                    "order": 789012,
                    "time": 1640995200,
                    "type": 0,
                    "entry": 0,
                    "magic": 0,
                    "position_id": 345678,
                    "reason": 0,
                    "volume": 0.1,
                    "price": 1.1300,
                    "commission": 0.0,
                    "swap": 0.0,
                    "profit": 10.0,
                    "fee": 0.0,
                    "symbol": "EURUSD",
                    "comment": "",
                    "external_id": "",
                }

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_get.return_value = [MockDealNoTimeMsc()]

        client.initialize()
        df_result = client.history_deals_get(
            datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 2, tzinfo=UTC)
        )

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert "time_msc" not in df_result.columns
