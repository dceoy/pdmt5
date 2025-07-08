"""Tests for pdmt5.manipulator module."""

# pyright: reportPrivateUsage=false

from collections.abc import Generator
from datetime import UTC, datetime
from types import ModuleType
from typing import NamedTuple

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from pdmt5.manipulator import Mt5Config, Mt5DataClient, Mt5Error

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
        mock_mt5.orders_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.positions_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_deals_get = mocker.MagicMock()  # type: ignore[attr-defined]
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


class TestMt5Config:
    """Test Mt5Config class."""

    def test_default_config(self):
        """Test default configuration."""
        config = Mt5Config()  # pyright: ignore[reportCallIssue]
        assert config.login is None
        assert config.password is None
        assert config.server is None
        assert config.timeout == 60000
        assert config.portable is False

    def test_custom_config(self):
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

    def test_config_immutable(self):
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
            login=123456, password="test", server="test-server", timeout=30000
        )
        client = Mt5DataClient(mt5=mock_mt5_import, config=config)
        assert client.config == config
        assert client.config.login == 123456
        assert client.config.timeout == 30000

    def test_missing_mt5_module(self):
        """Test initialization without providing mt5 module."""
        with pytest.raises(ValidationError, match="Field required"):
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
            Mt5Error, match="MetaTrader5 initialization failed: 1 - Connection failed"
        ):
            client.initialize()

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
        df = client.account_info()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["login"] == 123456
        assert df.iloc[0]["balance"] == 10000.0
        assert df.iloc[0]["currency"] == "USD"

    def test_account_info_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test account_info method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.account_info.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Account info failed")

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        with pytest.raises(
            Mt5Error, match="account_info failed: 1 - Account info failed"
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
        df = client.copy_rates_from("EURUSD", 1, datetime(2022, 1, 1, tzinfo=UTC), 2)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.iloc[0]["open"] == 1.1300
        assert df.iloc[0]["close"] == 1.1320
        assert df.iloc[1]["open"] == 1.1320
        assert df.iloc[1]["close"] == 1.1360

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
        df = client.copy_ticks_from("EURUSD", datetime(2022, 1, 1, tzinfo=UTC), 2, 6)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.iloc[0]["bid"] == 1.1300
        assert df.iloc[0]["ask"] == 1.1302
        assert df.iloc[1]["bid"] == 1.1301
        assert df.iloc[1]["ask"] == 1.1303

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
            )
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbols_get.return_value = mock_symbols

        client.initialize()
        df = client.symbols_get()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["name"] == "EURUSD"
        assert df.iloc[0]["currency_base"] == "EUR"
        assert df.iloc[0]["currency_profit"] == "USD"

    def test_orders_get_empty(self, mock_mt5_import: ModuleType | None) -> None:
        """Test orders_get method with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_get.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        df = client.orders_get()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_positions_get_empty(self, mock_mt5_import: ModuleType | None) -> None:
        """Test positions_get method with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_get.return_value = None

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        df = client.positions_get()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_error_handling_without_mt5(self):
        """Test error handling when MetaTrader5 module is not provided."""
        with pytest.raises(ValidationError, match="Field required"):
            Mt5DataClient()  # pyright: ignore[reportCallIssue]

    def test_ensure_initialized_calls_initialize(
        self, mock_mt5_import: ModuleType | None
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
        df = client.account_info()

        assert client._is_initialized is True
        mock_mt5_import.initialize.assert_called_once()
        assert isinstance(df, pd.DataFrame)

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
            )
        ]

        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_get.return_value = mock_deals

        client.initialize()
        df = client.history_deals_get(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
            symbol="EURUSD",
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["ticket"] == 123456
        assert df.iloc[0]["symbol"] == "EURUSD"
        assert df.iloc[0]["volume"] == 0.1
        assert df.iloc[0]["profit"] == 10.0
        # Check that time columns are converted to datetime
        assert isinstance(df.iloc[0]["time"], pd.Timestamp)
        assert isinstance(df.iloc[0]["time_msc"], pd.Timestamp)
