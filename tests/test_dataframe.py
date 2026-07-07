"""Tests for pdmt5.dataframe module."""

from collections.abc import Callable, Generator
from datetime import UTC, datetime
from types import ModuleType
from typing import Any, NamedTuple, cast

import numpy as np
import pandas as pd
import pytest
from pydantic import SecretStr, ValidationError
from pytest_mock import MockerFixture

from pdmt5.dataframe import Mt5Config, Mt5DataClient
from pdmt5.mt5 import Mt5Client, Mt5RuntimeError
from pdmt5.utils import (
    detect_and_convert_time_to_datetime,
)
from tests.helpers import create_mock_mt5_module

# Rebuild models to ensure they are fully defined for testing
Mt5DataClient.model_rebuild()

_MT5_METHODS = (
    "initialize",
    "shutdown",
    "last_error",
    "account_info",
    "terminal_info",
    "symbols_get",
    "symbol_info",
    "copy_rates_from",
    "copy_ticks_from",
    "copy_rates_from_pos",
    "copy_rates_range",
    "copy_ticks_range",
    "symbol_info_tick",
    "orders_get",
    "positions_get",
    "history_deals_get",
    "history_orders_get",
    "login",
    "order_check",
    "order_send",
    "orders_total",
    "positions_total",
    "history_orders_total",
    "history_deals_total",
    "order_calc_margin",
    "order_calc_profit",
    "version",
    "symbols_total",
    "symbol_select",
    "market_book_add",
    "market_book_release",
    "market_book_get",
)
_MASKED_SECRET = "*" * 10


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
    if (
        "initialize_import_error" in node_name
        or "test_error_handling_without_mt5" in node_name
    ):
        yield None
        return

    yield create_mock_mt5_module(
        mocker,
        methods=_MT5_METHODS,
        constants={"RES_S_OK": 1},
    )


def create_initialized_client(mock_mt5_import: ModuleType) -> Mt5DataClient:
    """Create an initialized dataframe client."""
    mock_mt5_import.initialize.return_value = True
    client = Mt5DataClient(mt5=mock_mt5_import)
    client.initialize()
    return client


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


def _create_mock_rates() -> np.ndarray[Any, np.dtype[Any]]:
    """Return a minimal mock rates array for copy_rates_* tests."""
    rate_dtype = np.dtype([
        ("time", "int64"),
        ("open", "float64"),
        ("high", "float64"),
        ("low", "float64"),
        ("close", "float64"),
    ])
    return np.array(
        [(1640995200, 1.1300, 1.1350, 1.1280, 1.1320)],
        dtype=rate_dtype,
    )


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


class _MockOrderNoTimeExpiration:
    """Mock order row omitting the time_expiration column."""

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


class _MockPositionNoTimeUpdate:
    """Mock position row omitting the time_update column."""

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


class _MockOrderNoTimeDone:
    """Mock history order row omitting the time_done column."""

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


def _mock_order_no_time_expiration() -> object:
    """Factory for an order row without time_expiration."""
    return _MockOrderNoTimeExpiration()


def _mock_position_no_time_update() -> object:
    """Factory for a position row without time_update."""
    return _MockPositionNoTimeUpdate()


def _mock_order_no_time_done() -> object:
    """Factory for a history order row without time_done."""
    return _MockOrderNoTimeDone()


def _build_history_order_row(position_id: int) -> MockOrder:
    """Build a history order row with the given position_id."""
    return MockOrder(
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
        position_id=position_id,
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
    )


def _build_history_deal_row(position_id: int) -> MockDeal:
    """Build a history deal row with the given position_id."""
    return MockDeal(
        ticket=123456,
        order=789012,
        time=1640995200,
        time_msc=1640995200000,
        type=0,
        entry=0,
        magic=0,
        position_id=position_id,
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
    )


class _MockSymbolRow:
    """Mock symbol row with a minimal set of fields, including time columns."""

    def _asdict(self) -> dict[str, Any]:
        return {
            "name": "EURUSD",
            "time": 1640995200,
            "time_msc": 1640995200000,
            "time_digits": 1640995200,
            "bid": 1.1300,
            "ask": 1.1301,
        }


class TestMt5Config:
    """Test Mt5Config class."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = Mt5Config()
        assert config.path is None
        assert config.login is None
        assert config.password is None
        assert config.server is None
        assert config.timeout is None

    @pytest.mark.parametrize(
        "password_input",
        [
            "secret",
            SecretStr("secret"),
        ],
        ids=["str-password", "secretstr-password"],
    )
    def test_config_password_coercion(self, password_input: str | SecretStr) -> None:
        """Test Mt5Config coerces password inputs to SecretStr."""
        config = Mt5Config(
            login=123456,
            password=password_input,
            server="Demo-Server",
            timeout=30000,
        )
        assert config.login == 123456
        assert isinstance(config.password, SecretStr)
        assert config.password.get_secret_value() == "secret"
        assert config.server == "Demo-Server"
        assert config.timeout == 30000

    def test_config_immutable(self) -> None:
        """Test that config is immutable."""
        config = Mt5Config()
        with pytest.raises(ValidationError):
            config.login = 123456

    def test_config_masks_password_in_string_representations(self) -> None:
        """Test SecretStr masks the password in printable config output."""
        config = Mt5Config(password="secret")
        dumped_password = config.model_dump()["password"]

        assert "secret" not in repr(config)
        assert "secret" not in str(config)
        assert "secret" not in repr(config.model_dump())
        assert isinstance(dumped_password, SecretStr)
        assert str(dumped_password) == _MASKED_SECRET
        assert config.model_dump(mode="json")["password"] == _MASKED_SECRET


class TestMt5DataClient:
    """Test Mt5DataClient class."""

    def test_init_default(self, mock_mt5_import: ModuleType | None) -> None:
        """Test client initialization with default config."""
        assert mock_mt5_import is not None
        client = Mt5DataClient(mt5=mock_mt5_import)
        assert client.config is not None
        assert client.config.timeout is None
        assert not client._is_initialized  # type: ignore[reportPrivateUsage]

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
        assert isinstance(client.config.password, SecretStr)
        assert client.config.password.get_secret_value() == "test"
        assert client.config.timeout == 30000

    def test_client_masks_nested_password_in_dumps(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test nested client config dumps do not expose a literal password."""
        assert mock_mt5_import is not None
        client = Mt5DataClient(
            mt5=mock_mt5_import,
            config=Mt5Config(password="secret"),
        )
        dumped_password = client.model_dump()["config"]["password"]

        assert "secret" not in repr(client)
        assert "secret" not in str(client)
        assert "secret" not in repr(client.model_dump())
        assert isinstance(dumped_password, SecretStr)
        assert str(dumped_password) == _MASKED_SECRET
        assert (
            client.model_dump(mode="json", exclude={"mt5"})["config"]["password"]
            == _MASKED_SECRET
        )

    def test_mt5_module_default_factory(self, mocker: MockerFixture) -> None:
        """Test initialization with default mt5 module factory."""
        # Mock the importlib.import_module to verify it's called
        mock_import = mocker.patch("importlib.import_module")
        mock_import.return_value = mocker.MagicMock()

        client = Mt5DataClient()

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
        assert client._is_initialized is True  # type: ignore[reportPrivateUsage]
        mock_mt5_import.initialize.assert_called_once()

    def test_initialize_failure(self, mock_mt5_import: ModuleType | None) -> None:
        """Test initialization failure."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = False
        mock_mt5_import.last_error.return_value = (1, "Connection failed")

        client = Mt5DataClient(mt5=mock_mt5_import, retry_count=0)
        pattern = (
            r"MT5 initialize and login failed after 0 retries: "
            r"\(1, 'Connection failed'\)"
        )
        with pytest.raises(Mt5RuntimeError, match=pattern):
            client.initialize_and_login_mt5()

    def test_initialize_already_initialized(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test initialize when already initialized."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        client = Mt5DataClient(mt5=mock_mt5_import)
        # Set _is_initialized to True to test the early return path
        client._is_initialized = True  # type: ignore[reportPrivateUsage]

        # Call initialize when already initialized - should still call mt5.initialize
        result = client.initialize()

        assert result is True  # Method returns True when successful
        mock_mt5_import.initialize.assert_called_once()

    def test_shutdown(self, mock_mt5_import: ModuleType | None) -> None:
        """Test shutdown."""
        assert mock_mt5_import is not None
        client = create_initialized_client(mock_mt5_import)
        client.shutdown()

        assert client._is_initialized is False  # type: ignore[reportPrivateUsage]
        mock_mt5_import.shutdown.assert_called_once()

    def test_context_manager(self, mock_mt5_import: ModuleType | None) -> None:
        """Test context manager functionality."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        with Mt5DataClient(mt5=mock_mt5_import) as client:
            assert client._is_initialized is True  # type: ignore[reportPrivateUsage]
            mock_mt5_import.initialize.assert_called_once()

        mock_mt5_import.shutdown.assert_called_once()

    def test_context_manager_uses_config_and_retries(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test context manager uses config credentials and retry_count."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.side_effect = [False, True]
        mock_mt5_import.login.return_value = True
        config = Mt5Config(
            path="/path/to/mt5.exe",
            login=123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )

        with Mt5DataClient(
            mt5=mock_mt5_import,
            config=config,
            retry_count=1,
        ) as client:
            assert client._is_initialized is True  # type: ignore[reportPrivateUsage]

        assert mock_mt5_import.initialize.call_count == 2
        mock_mt5_import.initialize.assert_any_call(
            "/path/to/mt5.exe",
            login=123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )
        mock_mt5_import.login.assert_called_once_with(
            123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )
        mock_mt5_import.shutdown.assert_called_once()

    def test_context_manager_shuts_down_after_login_failure(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test context manager cleans up initialized MT5 state after login failure."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.return_value = False
        mock_mt5_import.last_error.return_value = (1, "Login failed")
        config = Mt5Config(
            login=123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )

        with (
            pytest.raises(
                Mt5RuntimeError,
                match=r"MT5 initialize and login failed after 0 retries:",
            ),
            Mt5DataClient(
                mt5=mock_mt5_import,
                config=config,
                retry_count=0,
            ),
        ):
            pass

        mock_mt5_import.shutdown.assert_called_once()

    def test_initialize_and_login_retries_after_login_failure(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test login failure triggers cleanup before a successful retry."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.side_effect = [True, True]
        mock_mt5_import.login.side_effect = [False, True]
        config = Mt5Config(
            login=123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )
        client = Mt5DataClient(
            mt5=mock_mt5_import,
            config=config,
            retry_count=1,
        )

        client.initialize_and_login_mt5()

        assert mock_mt5_import.initialize.call_count == 2
        assert mock_mt5_import.login.call_count == 2
        mock_mt5_import.shutdown.assert_called_once()

    def test_initialize_and_login_reports_login_error_before_shutdown(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test the raised error embeds the login failure read before shutdown."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.return_value = False

        def last_error_side_effect() -> tuple[int, str]:
            if mock_mt5_import.shutdown.called:
                return (10004, "No IPC connection")
            return (-6, "Terminal: Authorization failed")

        mock_mt5_import.last_error.side_effect = last_error_side_effect
        config = Mt5Config(
            login=123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )
        client = Mt5DataClient(
            mt5=mock_mt5_import,
            config=config,
            retry_count=0,
        )

        pattern = (
            r"MT5 initialize and login failed after 0 retries: "
            r"\(-6, 'Terminal: Authorization failed'\)"
        )
        with pytest.raises(Mt5RuntimeError, match=pattern):
            client.initialize_and_login_mt5()

        mock_mt5_import.shutdown.assert_called_once()

    def test_initialize_and_login_shuts_down_after_login_exception(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test login exceptions trigger shutdown before the error is re-raised."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.side_effect = RuntimeError("Login crashed")
        config = Mt5Config(
            login=123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )
        client = Mt5DataClient(
            mt5=mock_mt5_import,
            config=config,
            retry_count=0,
        )

        with pytest.raises(Mt5RuntimeError, match=r"MT5 login failed with error:"):
            client.initialize_and_login_mt5()

        mock_mt5_import.shutdown.assert_called_once()

    def test_initialize_and_login_unwraps_secret_password_override(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test SecretStr overrides are unwrapped before MT5 calls."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.return_value = True
        client = Mt5DataClient(mt5=mock_mt5_import, retry_count=0)

        client.initialize_and_login_mt5(
            login=123456,
            password=SecretStr("secret"),
            server="Demo",
            timeout=60000,
        )

        mock_mt5_import.initialize.assert_called_once_with(
            login=123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )
        mock_mt5_import.login.assert_called_once_with(
            123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )

    @pytest.mark.parametrize(
        ("client_method", "mt5_method"),
        [
            ("orders_get_as_df", "orders_get"),
            ("positions_get_as_df", "positions_get"),
        ],
    )
    def test_orders_positions_get_empty(
        self, mock_mt5_import: ModuleType | None, client_method: str, mt5_method: str
    ) -> None:
        """Test orders_get/positions_get methods with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, mt5_method).return_value = []

        client = create_initialized_client(mock_mt5_import)
        df_result = getattr(client, client_method)()
        assert df_result.empty
        assert isinstance(df_result, pd.DataFrame)

    def test_error_handling_without_mt5(self) -> None:
        """Test error handling when an invalid mt5 module is provided."""
        # Test with an invalid mt5 module object
        invalid_mt5 = object()  # Not a proper module
        with pytest.raises(ValidationError):
            Mt5DataClient(mt5=cast("ModuleType", invalid_mt5))

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

        assert client._is_initialized is True  # type: ignore[reportPrivateUsage]
        mock_mt5_import.initialize.assert_called_once()
        assert isinstance(df_result, pd.DataFrame)

    def test_terminal_info_as_df(self, mock_mt5_import: ModuleType | None) -> None:
        """Test terminal_info_as_df method."""
        assert mock_mt5_import is not None

        class MockTerminalInfo:
            def _asdict(self) -> dict[str, Any]:
                return {"name": "MetaTrader 5", "version": 123}

        mock_mt5_import.terminal_info.return_value = MockTerminalInfo()

        client = create_initialized_client(mock_mt5_import)
        df_result = client.terminal_info_as_df()

        mock_mt5_import.initialize.assert_called_once()
        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert "name" in df_result.columns
        assert "version" in df_result.columns

    @pytest.mark.parametrize(
        (
            "client_method",
            "mt5_method",
            "row",
            "volume_col",
            "time_col",
            "time_msc_col",
        ),
        [
            pytest.param(
                "orders_get_as_df",
                "orders_get",
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
                "volume_initial",
                "time_setup",
                "time_setup_msc",
                id="orders_get",
            ),
            pytest.param(
                "positions_get_as_df",
                "positions_get",
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
                "volume",
                "time",
                "time_msc",
                id="positions_get",
            ),
        ],
    )
    def test_orders_positions_get_with_data(
        self,
        mock_mt5_import: ModuleType | None,
        client_method: str,
        mt5_method: str,
        row: object,
        volume_col: str,
        time_col: str,
        time_msc_col: str,
    ) -> None:
        """Test orders_get_as_df/positions_get_as_df methods with data."""
        assert mock_mt5_import is not None
        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, mt5_method).return_value = [row]

        client.initialize()
        df_result = getattr(client, client_method)(symbol="EURUSD", index_keys="ticket")

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert df_result.index[0] == 123456
        assert df_result.iloc[0]["symbol"] == "EURUSD"
        assert df_result.iloc[0][volume_col] == pytest.approx(0.1)
        assert df_result.iloc[0][time_col] == pd.to_datetime(1640995200, unit="s")
        assert df_result.iloc[0][time_msc_col] == pd.to_datetime(
            1640995200000, unit="ms"
        )

    @pytest.mark.parametrize(
        ("timeout", "expected_kwargs"),
        [
            (None, {"password": "password", "server": "server.com"}),
            (30000, {"password": "password", "server": "server.com", "timeout": 30000}),
        ],
    )
    def test_login_success(
        self,
        mock_mt5_import: ModuleType | None,
        timeout: int | None,
        expected_kwargs: dict[str, Any],
    ) -> None:
        """Test login method success with and without timeout."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.return_value = True

        client = create_initialized_client(mock_mt5_import)
        result = client.login(123456, "password", "server.com", timeout=timeout)

        assert result is True
        mock_mt5_import.login.assert_called_once_with(123456, **expected_kwargs)

    def test_login_failure(self, mock_mt5_import: ModuleType | None) -> None:
        """Test login method failure."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.login.return_value = False

        client = create_initialized_client(mock_mt5_import)
        result = client.login(123456, "password", "server.com")

        assert result is False

    @pytest.mark.parametrize(
        ("client_method", "mt5_method", "return_value"),
        [
            ("orders_total", "orders_total", 5),
            ("positions_total", "positions_total", 3),
            ("symbols_total", "symbols_total", 1000),
        ],
    )
    def test_total_methods(
        self,
        mock_mt5_import: ModuleType | None,
        client_method: str,
        mt5_method: str,
        return_value: int,
    ) -> None:
        """Test total-returning methods with values."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, mt5_method).return_value = return_value

        client = create_initialized_client(mock_mt5_import)
        result = getattr(client, client_method)()

        assert result == return_value

    @pytest.mark.parametrize(
        "method_name", ["orders_total", "positions_total", "symbols_total"]
    )
    def test_total_methods_raise_on_none(
        self, mock_mt5_import: ModuleType | None, method_name: str
    ) -> None:
        """Test total-returning methods raise Mt5RuntimeError on None."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, method_name).return_value = None

        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(Mt5RuntimeError, match=rf"MT5 {method_name} returned None"):
            getattr(client, method_name)()

    @pytest.mark.parametrize(
        ("client_method", "mt5_method", "return_value"),
        [
            ("history_orders_total", "history_orders_total", 10),
            ("history_orders_total", "history_orders_total", 0),
            ("history_deals_total", "history_deals_total", 15),
            ("history_deals_total", "history_deals_total", 0),
        ],
    )
    def test_history_totals_methods(
        self,
        mock_mt5_import: ModuleType | None,
        client_method: str,
        mt5_method: str,
        return_value: int,
    ) -> None:
        """Test history total methods with varied return values."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, mt5_method).return_value = return_value

        client = create_initialized_client(mock_mt5_import)
        result = getattr(client, client_method)(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )

        assert result == return_value

    @pytest.mark.parametrize(
        "method_name", ["history_orders_total", "history_deals_total"]
    )
    def test_history_totals_methods_raise_on_none(
        self, mock_mt5_import: ModuleType | None, method_name: str
    ) -> None:
        """Test history total methods raise Mt5RuntimeError on None."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, method_name).return_value = None

        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(Mt5RuntimeError, match=rf"MT5 {method_name} returned None"):
            getattr(client, method_name)(
                datetime(2022, 1, 1, tzinfo=UTC),
                datetime(2022, 1, 2, tzinfo=UTC),
            )

    @pytest.mark.parametrize(
        ("volume", "price", "last_error"),
        [
            (0.1, 1.1300, None),
            (0.0, 1.1300, "Invalid volume"),
            (0.1, 0.0, "Invalid price"),
            (0.1, 1.1300, "Order calc margin failed"),
        ],
    )
    def test_order_calc_margin(
        self,
        mock_mt5_import: ModuleType | None,
        volume: float,
        price: float,
        last_error: str | None,
    ) -> None:
        """Test order_calc_margin with success and failure paths."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_margin.return_value = (
            100.0 if last_error is None else None
        )
        if last_error is not None:
            mock_mt5_import.last_error.return_value = (1, last_error)

        client = create_initialized_client(mock_mt5_import)

        if last_error is None:
            result = client.order_calc_margin(0, "EURUSD", volume, price)
            assert result == pytest.approx(100.0)
        else:
            with pytest.raises(
                Mt5RuntimeError, match=r"MT5 order_calc_margin returned None"
            ):
                client.order_calc_margin(0, "EURUSD", volume, price)

    def test_order_calc_profit(self, mock_mt5_import: ModuleType | None) -> None:
        """Test order_calc_profit method."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_profit.return_value = 10.0

        client = create_initialized_client(mock_mt5_import)
        result = client.order_calc_profit(0, "EURUSD", 0.1, 1.1300, 1.1400)

        assert result == pytest.approx(10.0)

    @pytest.mark.parametrize(
        ("args", "last_error", "context_substr"),
        [
            pytest.param(
                (0, "EURUSD", 0.0, 1.1300, 1.1400),
                (1, "Invalid volume"),
                "volume=0.0",
                id="invalid-volume",
            ),
            pytest.param(
                (0, "EURUSD", 0.1, 0.0, 1.1400),
                (1, "Invalid price_open"),
                "price_open=0.0",
                id="invalid-price-open",
            ),
            pytest.param(
                (0, "EURUSD", 0.1, 1.1300, 0.0),
                (1, "Invalid price_close"),
                "price_close=0.0",
                id="invalid-price-close",
            ),
            pytest.param(
                (0, "EURUSD", 0.1, 1.1300, 1.1400),
                (1, "Order calc profit failed"),
                "Order calc profit failed",
                id="mt5-error",
            ),
        ],
    )
    def test_order_calc_profit_returns_none(
        self,
        mock_mt5_import: ModuleType | None,
        args: tuple[int, str, float, float, float],
        last_error: tuple[int, str],
        context_substr: str,
    ) -> None:
        """Test order_calc_profit raises Mt5RuntimeError with per-case context."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.order_calc_profit.return_value = None
        mock_mt5_import.last_error.return_value = last_error

        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(
            Mt5RuntimeError, match=r"MT5 order_calc_profit returned None"
        ) as exc_info:
            client.order_calc_profit(*args)
        assert context_substr in str(exc_info.value)

    def test_version(self, mock_mt5_import: ModuleType | None) -> None:
        """Test version with a value."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.version.return_value = (2460, 2460, "15 Feb 2022")

        client = create_initialized_client(mock_mt5_import)
        result = client.version()

        assert result == (2460, 2460, "15 Feb 2022")

    def test_version_raises_on_none(self, mock_mt5_import: ModuleType | None) -> None:
        """Test version raises Mt5RuntimeError on None."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.version.return_value = None

        client = create_initialized_client(mock_mt5_import)

        with pytest.raises(Mt5RuntimeError, match=r"MT5 version failed with error:"):
            client.version()

    @pytest.mark.parametrize("enable", [True, False])
    def test_symbol_select(
        self, mock_mt5_import: ModuleType | None, enable: bool
    ) -> None:
        """Test symbol_select with and without enable flag."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_select.return_value = True

        client = create_initialized_client(mock_mt5_import)
        result = client.symbol_select("EURUSD", enable=enable)

        assert result is True

    def test_symbol_select_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test symbol_select method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_select.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Symbol select failed")

        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(Mt5RuntimeError, match=r"MT5 symbol_select returned None"):
            client.symbol_select("EURUSD")

    @pytest.mark.parametrize("method", ["market_book_add", "market_book_release"])
    def test_market_book_actions_success(
        self, mock_mt5_import: ModuleType | None, method: str
    ) -> None:
        """Test market_book_add/release success."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, method).return_value = True

        client = create_initialized_client(mock_mt5_import)
        result = getattr(client, method)("EURUSD")

        assert result is True

    @pytest.mark.parametrize("method", ["market_book_add", "market_book_release"])
    def test_market_book_actions_error(
        self, mock_mt5_import: ModuleType | None, method: str
    ) -> None:
        """Test market_book_add/release error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, method).return_value = None
        mock_mt5_import.last_error.return_value = (1, f"{method} failed")

        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(Mt5RuntimeError, match=rf"MT5 {method} returned None"):
            getattr(client, method)("EURUSD")

    @pytest.mark.parametrize(
        (
            "position_id",
            "call_kwargs",
            "expectation",
            "expected_mt5_args",
            "expected_mt5_kwargs",
        ),
        [
            pytest.param(
                0,
                {"ticket": 123456, "index_keys": "ticket"},
                ("index", 123456),
                (),
                {"ticket": 123456},
                id="ticket",
            ),
            pytest.param(
                345678,
                {"position": 345678},
                ("position_id", 345678),
                (),
                {"position": 345678},
                id="position",
            ),
            pytest.param(
                0,
                {
                    "date_from": datetime(2022, 1, 1, tzinfo=UTC),
                    "date_to": datetime(2022, 1, 2, tzinfo=UTC),
                    "symbol": "EURUSD",
                },
                ("symbol", "EURUSD"),
                (datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 2, tzinfo=UTC)),
                {"group": "*EURUSD*"},
                id="symbol",
            ),
            pytest.param(
                0,
                {
                    "date_from": datetime(2022, 1, 1, tzinfo=UTC),
                    "date_to": datetime(2022, 1, 2, tzinfo=UTC),
                    "group": "*USD*",
                },
                ("symbol", "EURUSD"),
                (datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 2, tzinfo=UTC)),
                {"group": "*USD*"},
                id="group",
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("client_method", "mt5_method", "row_factory"),
        [
            pytest.param(
                "history_orders_get_as_df",
                "history_orders_get",
                _build_history_order_row,
                id="orders",
            ),
            pytest.param(
                "history_deals_get_as_df",
                "history_deals_get",
                _build_history_deal_row,
                id="deals",
            ),
        ],
    )
    def test_history_get_filters(
        self,
        mock_mt5_import: ModuleType | None,
        client_method: str,
        mt5_method: str,
        row_factory: Callable[[int], object],
        position_id: int,
        call_kwargs: dict[str, Any],
        expectation: tuple[str, Any],
        expected_mt5_args: tuple[Any, ...],
        expected_mt5_kwargs: dict[str, Any],
    ) -> None:
        """Test history_orders_get_as_df/history_deals_get_as_df with filters."""
        assert mock_mt5_import is not None
        client = Mt5DataClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, mt5_method).return_value = [row_factory(position_id)]
        client.initialize()
        df_result = getattr(client, client_method)(**call_kwargs)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        key, val = expectation
        if key == "index":
            assert df_result.index[0] == val
        else:
            assert df_result.iloc[0][key] == val
        getattr(mock_mt5_import, mt5_method).assert_called_once_with(
            *expected_mt5_args, **expected_mt5_kwargs
        )

    @pytest.mark.parametrize(
        "client_method",
        ["history_orders_get_as_dicts", "history_deals_get_as_dicts"],
    )
    def test_history_get_symbol_and_group_conflict(
        self, mock_mt5_import: ModuleType | None, client_method: str
    ) -> None:
        """Test history getters reject combined symbol and group filters."""
        assert mock_mt5_import is not None
        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(
            ValueError, match=r"symbol and group filters are mutually exclusive"
        ):
            getattr(client, client_method)(
                date_from=datetime(2022, 1, 1, tzinfo=UTC),
                date_to=datetime(2022, 1, 2, tzinfo=UTC),
                symbol="EURUSD",
                group="*USD*",
            )

    @pytest.mark.parametrize(
        ("client_method", "mt5_method", "row_factory"),
        [
            pytest.param(
                "history_orders_get_as_df",
                "history_orders_get",
                _build_history_order_row,
                id="orders",
            ),
            pytest.param(
                "history_deals_get_as_df",
                "history_deals_get",
                _build_history_deal_row,
                id="deals",
            ),
        ],
    )
    def test_history_get_symbol_exact_match(
        self,
        mock_mt5_import: ModuleType | None,
        client_method: str,
        mt5_method: str,
        row_factory: Callable[[int], Any],
    ) -> None:
        """Test symbol filter excludes broker-suffixed symbol variants."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, mt5_method).return_value = [
            row_factory(0),
            row_factory(0)._replace(symbol="EURUSD.m"),
        ]

        client = create_initialized_client(mock_mt5_import)
        df_result = getattr(client, client_method)(
            date_from=datetime(2022, 1, 1, tzinfo=UTC),
            date_to=datetime(2022, 1, 2, tzinfo=UTC),
            symbol="EURUSD",
        )

        assert isinstance(df_result, pd.DataFrame)
        assert df_result["symbol"].tolist() == ["EURUSD"]
        getattr(mock_mt5_import, mt5_method).assert_called_once_with(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
            group="*EURUSD*",
        )

    @pytest.mark.parametrize(
        ("client_method", "mt5_method"),
        [
            pytest.param(
                "history_orders_get_as_df",
                "history_orders_get",
                id="history_orders",
            ),
            pytest.param(
                "history_deals_get_as_df",
                "history_deals_get",
                id="history_deals",
            ),
        ],
    )
    def test_history_get_no_dates(
        self,
        mock_mt5_import: ModuleType | None,
        client_method: str,
        mt5_method: str,
    ) -> None:
        """Test history methods without dates when not using ticket or position."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, mt5_method).return_value = []
        mock_mt5_import.last_error.return_value = (1, "Invalid arguments")

        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(
            ValueError,
            match=(
                r"Both date_from and date_to must be provided"
                r" if not using ticket or position"
            ),
        ):
            getattr(client, client_method)()

    def test_history_orders_get_invalid_dates(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test history_orders_get method with invalid date range."""
        assert mock_mt5_import is not None
        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(ValueError, match=r"Invalid date range"):
            client.history_orders_get_as_df(
                datetime(2022, 1, 2, tzinfo=UTC),
                datetime(2022, 1, 1, tzinfo=UTC),
            )

    def test_history_orders_get_empty(self, mock_mt5_import: ModuleType | None) -> None:
        """Test history_orders_get method with empty result."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = []

        client = create_initialized_client(mock_mt5_import)
        orders_df = client.history_orders_get_as_df(
            datetime(2022, 1, 1, tzinfo=UTC),
            datetime(2022, 1, 2, tzinfo=UTC),
        )
        assert orders_df.empty
        assert isinstance(orders_df, pd.DataFrame)

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
        assert result[0].price == pytest.approx(1.1300)
        assert result[1].type == 1
        assert result[1].price == pytest.approx(1.1302)

    def test_market_book_get_error(self, mock_mt5_import: ModuleType | None) -> None:
        """Test market_book_get method with error."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.market_book_get.return_value = None
        mock_mt5_import.last_error.return_value = (1, "Market book get failed")

        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(Mt5RuntimeError, match=r"MT5 market_book_get returned None"):
            client.market_book_get("EURUSD")

    def test_shutdown_when_not_initialized(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test shutdown method when already not initialized."""
        assert mock_mt5_import is not None

        client = Mt5DataClient(mt5=mock_mt5_import)
        # Don't initialize
        client.shutdown()  # Should call mt5.shutdown()

        mock_mt5_import.shutdown.assert_called_once()

    @pytest.mark.parametrize(
        (
            "client_method",
            "mt5_method",
            "row_factory",
            "missing_column",
            "extra_args",
        ),
        [
            pytest.param(
                "orders_get_as_df",
                "orders_get",
                _mock_order_no_time_expiration,
                "time_expiration",
                (),
                id="orders-missing-time_expiration",
            ),
            pytest.param(
                "positions_get_as_df",
                "positions_get",
                _mock_position_no_time_update,
                "time_update",
                (),
                id="positions-missing-time_update",
            ),
            pytest.param(
                "history_orders_get_as_df",
                "history_orders_get",
                _mock_order_no_time_done,
                "time_done",
                (datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 1, 2, tzinfo=UTC)),
                id="history-orders-missing-time_done",
            ),
        ],
    )
    def test_get_missing_time_columns(
        self,
        mock_mt5_import: ModuleType | None,
        client_method: str,
        mt5_method: str,
        row_factory: Callable[[], object],
        missing_column: str,
        extra_args: tuple[Any, ...],
    ) -> None:
        """Test DataFrame methods when expected time columns are missing."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True
        getattr(mock_mt5_import, mt5_method).return_value = [row_factory()]

        client = Mt5DataClient(mt5=mock_mt5_import)
        client.initialize()
        df_result = getattr(client, client_method)(*extra_args)

        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 1
        assert missing_column not in df_result.columns


class TestMt5DataClientValidation:
    """Test Mt5DataClient validation methods."""

    @pytest.mark.parametrize("count", [1, 100])
    def test_validate_positive_count_valid(self, count: int) -> None:
        """Test _validate_positive_count with valid counts."""
        Mt5DataClient._validate_positive_count(  # type: ignore[reportPrivateUsage]
            count=count
        )

    @pytest.mark.parametrize(
        ("count", "match"),
        [
            (0, r"Invalid count: 0\. Count must be positive\."),
            (-1, r"Invalid count: -1\. Count must be positive\."),
        ],
    )
    def test_validate_positive_count_invalid(self, count: int, match: str) -> None:
        """Test _validate_positive_count with invalid counts."""
        with pytest.raises(ValueError, match=match):
            Mt5DataClient._validate_positive_count(  # type: ignore[reportPrivateUsage]
                count=count
            )

    def test_validate_date_range_valid(self) -> None:
        """Test _validate_date_range with valid date range."""
        date_from = datetime(2023, 1, 1, tzinfo=UTC)
        date_to = datetime(2023, 1, 2, tzinfo=UTC)
        # Should not raise for valid date range
        Mt5DataClient._validate_date_range(  # type: ignore[reportPrivateUsage]
            date_from=date_from, date_to=date_to
        )

    def test_validate_date_range_invalid(self) -> None:
        """Test _validate_date_range with invalid date range."""
        date_from = datetime(2023, 1, 2, tzinfo=UTC)
        date_to = datetime(2023, 1, 1, tzinfo=UTC)
        with pytest.raises(
            ValueError, match=r"Invalid date range: from=.* must be before to=.*"
        ):
            Mt5DataClient._validate_date_range(  # type: ignore[reportPrivateUsage]
                date_from=date_from, date_to=date_to
            )

    @pytest.mark.parametrize(
        ("value", "name"),
        [
            (1.0, "volume"),
            (0.1, "volume"),
        ],
    )
    def test_validate_positive_value_valid(self, value: float, name: str) -> None:
        """Test _validate_positive_value with valid values."""
        Mt5DataClient._validate_positive_value(  # type: ignore[reportPrivateUsage]
            value=value,
            name=name,
        )

    @pytest.mark.parametrize(
        ("value", "name", "match"),
        [
            (0, "volume", r"Invalid volume: 0\. Volume must be positive\."),
            (-1, "volume", r"Invalid volume: -1\. Volume must be positive\."),
            (0, "price_open", r"Invalid price_open: 0\. Price must be positive\."),
            (-1, "price_close", r"Invalid price_close: -1\. Price must be positive\."),
        ],
    )
    def test_validate_positive_value_invalid(
        self, value: int, name: str, match: str
    ) -> None:
        """Test _validate_positive_value with invalid values."""
        with pytest.raises(ValueError, match=match):
            Mt5DataClient._validate_positive_value(  # type: ignore[reportPrivateUsage]
                value=value,
                name=name,
            )

    @pytest.mark.parametrize("position", [0, 10])
    def test_validate_non_negative_position_valid(self, position: int) -> None:
        """Test _validate_non_negative_position with valid positions."""
        Mt5DataClient._validate_non_negative_position(  # type: ignore[reportPrivateUsage]
            position=position
        )

    def test_validate_non_negative_position_invalid(self) -> None:
        """Test _validate_non_negative_position with invalid position."""
        with pytest.raises(
            ValueError,
            match=r"Invalid start_pos: -1\. Position must be non-negative\.",
        ):
            Mt5DataClient._validate_non_negative_position(  # type: ignore[reportPrivateUsage]
                position=-1
            )

    @pytest.mark.parametrize(
        ("client_method", "mt5_method", "extra_key", "extra_value"),
        [
            pytest.param(
                "order_check_as_dict",
                "order_check",
                "volume",
                1.0,
                id="order_check",
            ),
            pytest.param(
                "order_send_as_dict",
                "order_send",
                "order",
                12345,
                id="order_send",
            ),
        ],
    )
    def test_order_action_as_dict(
        self,
        mock_mt5_import: ModuleType,
        mocker: MockerFixture,
        client_method: str,
        mt5_method: str,
        extra_key: str,
        extra_value: int | float,  # noqa: PYI041
    ) -> None:
        """Test order_check_as_dict and order_send_as_dict methods."""
        config = Mt5Config()

        # Mock order action result with nested request structure
        mock_request = mocker.MagicMock()
        mock_request._asdict.return_value = {"action": 1, "symbol": "EURUSD"}

        mock_result = mocker.MagicMock()
        mock_result._asdict.return_value = {
            "retcode": 10009,
            "request": mock_request,
            extra_key: extra_value,
        }

        with Mt5DataClient(mt5=mock_mt5_import, config=config) as client:
            getattr(mock_mt5_import, mt5_method).return_value = mock_result

            result = getattr(client, client_method)(
                request={"action": 1, "symbol": "EURUSD"}
            )

            assert result["retcode"] == 10009
            assert result["request"] == {"action": 1, "symbol": "EURUSD"}
            if isinstance(extra_value, float):
                assert result[extra_key] == pytest.approx(extra_value)
            else:
                assert result[extra_key] == extra_value

    @pytest.mark.parametrize(
        ("client_method", "mt5_method", "call_kwargs"),
        [
            pytest.param(
                "copy_rates_from_as_df",
                "copy_rates_from",
                {
                    "symbol": "EURUSD",
                    "timeframe": 16385,
                    "date_from": datetime(2023, 1, 1, tzinfo=UTC),
                    "count": 1,
                    "index_keys": "time",
                },
                id="copy_rates_from-count-one",
            ),
            pytest.param(
                "copy_rates_from_as_df",
                "copy_rates_from",
                {
                    "symbol": "EURUSD",
                    "timeframe": 16385,
                    "date_from": datetime(2023, 1, 1, tzinfo=UTC),
                    "count": 10,
                    "index_keys": "time",
                },
                id="copy_rates_from-count-ten",
            ),
            pytest.param(
                "copy_rates_range_as_df",
                "copy_rates_range",
                {
                    "symbol": "EURUSD",
                    "timeframe": 16385,
                    "date_from": datetime(2023, 1, 1, tzinfo=UTC),
                    "date_to": datetime(2023, 1, 2, tzinfo=UTC),
                    "index_keys": "time",
                },
                id="copy_rates_range-one-day",
            ),
            pytest.param(
                "copy_rates_range_as_df",
                "copy_rates_range",
                {
                    "symbol": "EURUSD",
                    "timeframe": 16385,
                    "date_from": datetime(2023, 1, 1, tzinfo=UTC),
                    "date_to": datetime(2023, 1, 31, tzinfo=UTC),
                    "index_keys": "time",
                },
                id="copy_rates_range-one-month",
            ),
        ],
    )
    def test_copy_rates_as_df(
        self,
        mock_mt5_import: ModuleType,
        client_method: str,
        mt5_method: str,
        call_kwargs: dict[str, Any],
    ) -> None:
        """Test copy_rates_from_as_df and copy_rates_range_as_df."""
        config = Mt5Config()

        with Mt5DataClient(mt5=mock_mt5_import, config=config) as client:
            getattr(mock_mt5_import, mt5_method).return_value = _create_mock_rates()

            result = getattr(client, client_method)(**call_kwargs)

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
        client.initialize_and_login_mt5()

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
        client.initialize_and_login_mt5()

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
            client.initialize_and_login_mt5()

        assert "MT5 initialize and login failed after" in str(exc_info.value)
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
        assert dict_result["balance"] == pytest.approx(10000.0)
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
        assert dict_result["bid"] == pytest.approx(1.13200)
        assert dict_result["ask"] == pytest.approx(1.13210)
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
        assert dict_result["bid"] == pytest.approx(1.13200)
        assert dict_result["ask"] == pytest.approx(1.13210)
        assert dict_result["last"] == pytest.approx(1.13205)
        assert dict_result["volume"] == 100
        assert dict_result["time"] == pd.to_datetime(1640995200, unit="s")
        assert dict_result["flags"] == 134

    @pytest.mark.parametrize(
        "method_name",
        [
            # Inherited from Mt5Client
            "initialize",
            "shutdown",
            "account_info",
            "terminal_info",
            "symbol_info",
            "symbol_info_tick",
            "copy_rates_from",
            "copy_rates_from_pos",
            "copy_rates_range",
            "copy_ticks_from",
            "copy_ticks_range",
            "orders_get",
            "positions_get",
            "history_orders_get",
            "history_deals_get",
            # Added by Mt5DataClient
            "account_info_as_df",
            "terminal_info_as_df",
            "copy_rates_from_as_df",
            "copy_rates_from_pos_as_df",
            "copy_rates_range_as_df",
            "copy_ticks_from_as_df",
            "copy_ticks_range_as_df",
            "symbols_get_as_df",
            "orders_get_as_df",
            "positions_get_as_df",
            "history_orders_get_as_df",
            "history_deals_get_as_df",
        ],
    )
    def test_inheritance_exposes_expected_methods(
        self, mock_mt5_import: ModuleType | None, method_name: str
    ) -> None:
        """Test Mt5DataClient exposes inherited and DataFrame helper methods."""
        assert mock_mt5_import is not None
        client = Mt5DataClient(mt5=mock_mt5_import)

        assert hasattr(client, method_name)

    def test_inheritance_behavior(self, mock_mt5_import: ModuleType | None) -> None:
        """Test that Mt5DataClient properly inherits parent-class behavior."""
        assert mock_mt5_import is not None
        client = Mt5DataClient(mt5=mock_mt5_import)

        assert isinstance(client, Mt5Client)

        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.last_error.return_value = (0, "No error")

        result = client.initialize()
        assert result is True
        mock_mt5_import.initialize.assert_called_once()

        # Test last_error method from parent class
        error = client.last_error()
        assert error == (0, "No error")
        # last_error is called multiple times (in decorators and explicitly)
        assert mock_mt5_import.last_error.call_count >= 1

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"ticket": 123456},
            {"position": 789012},
            {
                "date_from": datetime(2022, 1, 1, tzinfo=UTC),
                "date_to": datetime(2022, 1, 2, tzinfo=UTC),
            },
        ],
    )
    def test_validate_history_input_valid(
        self,
        mock_mt5_import: ModuleType | None,
        kwargs: dict[str, Any],
    ) -> None:
        """Test _validate_history_input with valid inputs."""
        assert mock_mt5_import is not None
        client = create_initialized_client(mock_mt5_import)
        client._validate_history_input(**kwargs)  # type: ignore[reportPrivateUsage]

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"date_from": datetime(2022, 1, 1, tzinfo=UTC)},
            {"date_to": datetime(2022, 1, 2, tzinfo=UTC)},
            {},
        ],
    )
    def test_validate_history_input_invalid(
        self,
        mock_mt5_import: ModuleType | None,
        kwargs: dict[str, Any],
    ) -> None:
        """Test _validate_history_input rejects missing or incomplete date inputs."""
        assert mock_mt5_import is not None
        client = create_initialized_client(mock_mt5_import)
        with pytest.raises(
            ValueError,
            match=(
                r"Both date_from and date_to must be provided"
                r" if not using ticket or position"
            ),
        ):
            client._validate_history_input(**kwargs)  # type: ignore[reportPrivateUsage]

    def test_context_manager_with_exception(
        self, mock_mt5_import: ModuleType | None
    ) -> None:
        """Test context manager handles exceptions properly."""
        assert mock_mt5_import is not None
        mock_mt5_import.initialize.return_value = True

        test_exception_msg = "Test exception"
        with Mt5DataClient(mt5=mock_mt5_import) as client:
            assert client._is_initialized is True  # type: ignore[reportPrivateUsage]
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
        assert client._is_initialized is True  # type: ignore[reportPrivateUsage]
        mock_mt5_import.initialize.assert_called_once()

        # Reset the mock
        mock_mt5_import.initialize.reset_mock()

        # Call initialize again - should still call mt5.initialize()
        client.initialize()

        # Initialize should be called again in current implementation
        mock_mt5_import.initialize.assert_called_once()
        # The method should still return True (or whatever the expected behavior is)
        assert client._is_initialized is True  # type: ignore[reportPrivateUsage]


class TestMt5DataClientCoverageMissing:
    """Test class for missing coverage methods."""

    def test_version_as_df(self, mock_mt5_import: ModuleType) -> None:
        """Test version_as_df method."""
        mock_mt5_import.version.return_value = (123, 456, "build")
        client = create_initialized_client(mock_mt5_import)

        result = client.version_as_df()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "mt5_terminal_version" in result.columns
        assert "build" in result.columns

    @pytest.mark.parametrize("client_method", ["version_as_dict", "version_as_df"])
    def test_version_methods_raise_mt5_runtime_error_on_none_response(
        self, mock_mt5_import: ModuleType, client_method: str
    ) -> None:
        """Test version dictionary/dataframe helpers raise Mt5RuntimeError on None."""
        mock_mt5_import.version.return_value = None
        client = create_initialized_client(mock_mt5_import)

        with pytest.raises(Mt5RuntimeError, match=r"MT5 version failed with error:"):
            getattr(client, client_method)()

    def test_last_error_as_dict(self, mock_mt5_import: ModuleType) -> None:
        """Test last_error_as_dict method."""
        mock_mt5_import.last_error.return_value = (123, "Test error")
        client = Mt5DataClient(mt5=mock_mt5_import)

        result = client.last_error_as_dict()

        assert isinstance(result, dict)
        assert result["error_code"] == 123
        assert result["error_description"] == "Test error"

    def test_last_error_as_df(self, mock_mt5_import: ModuleType) -> None:
        """Test last_error_as_df method."""
        mock_mt5_import.last_error.return_value = (456, "Another error")
        client = Mt5DataClient(mt5=mock_mt5_import)

        result = client.last_error_as_df()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "error_code" in result.columns
        assert "error_description" in result.columns
        assert result.iloc[0]["error_code"] == 456
        assert result.iloc[0]["error_description"] == "Another error"

    def test_symbol_info_as_df(self, mock_mt5_import: ModuleType) -> None:
        """Test symbol_info_as_df method."""

        class MockSymbolInfo(NamedTuple):
            symbol: str
            bid: float
            ask: float

        mock_symbol_info = MockSymbolInfo(symbol="EURUSD", bid=1.1000, ask=1.1001)
        mock_mt5_import.symbol_info.return_value = mock_symbol_info
        client = create_initialized_client(mock_mt5_import)

        result = client.symbol_info_as_df("EURUSD")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "symbol" in result.columns
        assert "bid" in result.columns
        assert "ask" in result.columns

    def test_symbol_info_tick_as_df(self, mock_mt5_import: ModuleType) -> None:
        """Test symbol_info_tick_as_df method."""

        class MockTick(NamedTuple):
            time: int
            bid: float
            ask: float

        mock_tick = MockTick(time=1640995200, bid=1.1000, ask=1.1001)
        mock_mt5_import.symbol_info_tick.return_value = mock_tick
        client = create_initialized_client(mock_mt5_import)

        result = client.symbol_info_tick_as_df("EURUSD")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "time" in result.columns
        assert "bid" in result.columns
        assert "ask" in result.columns

    def test_market_book_get_as_df(self, mock_mt5_import: ModuleType) -> None:
        """Test market_book_get_as_df method."""

        class MockBookInfo(NamedTuple):
            type: int
            price: float
            volume: float

        mock_book_data = [
            MockBookInfo(type=1, price=1.1000, volume=100.0),
            MockBookInfo(type=2, price=1.1001, volume=200.0),
        ]
        mock_mt5_import.market_book_get.return_value = mock_book_data
        client = create_initialized_client(mock_mt5_import)

        result = client.market_book_get_as_df("EURUSD", index_keys="price")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "type" in result.columns
        assert "volume" in result.columns
        # Price is used as index in market book data
        assert result.index.name == "price"

    @pytest.mark.parametrize(
        ("client_method", "mt5_method", "extra_columns"),
        [
            pytest.param(
                "order_check_as_df",
                "order_check",
                ("margin", "profit"),
                id="order_check",
            ),
            pytest.param(
                "order_send_as_df",
                "order_send",
                ("deal", "order"),
                id="order_send",
            ),
        ],
    )
    def test_order_action_as_df(
        self,
        mock_mt5_import: ModuleType,
        mocker: MockerFixture,
        client_method: str,
        mt5_method: str,
        extra_columns: tuple[str, ...],
    ) -> None:
        """Test order_check_as_df and order_send_as_df methods."""
        client = create_initialized_client(mock_mt5_import)

        mock_request = mocker.MagicMock()
        mock_request._asdict.return_value = {"action": 1, "symbol": "EURUSD"}

        mock_result = mocker.MagicMock()
        mock_result._asdict.return_value = {
            "retcode": 10009,
            "request": mock_request,
            **dict.fromkeys(extra_columns, 0),
        }
        getattr(mock_mt5_import, mt5_method).return_value = mock_result

        request = {"action": 1, "symbol": "EURUSD", "volume": 0.1}
        result = getattr(client, client_method)(request)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "retcode" in result.columns
        for col in extra_columns:
            assert col in result.columns

    @pytest.mark.parametrize(
        ("input_dict", "kwargs", "expected"),
        [
            ({"a": 1, "b": 2, "c": 3}, {}, {"a": 1, "b": 2, "c": 3}),
            (
                {"a": 1, "nested": {"x": 10, "y": 20}, "b": 2},
                {},
                {"a": 1, "nested_x": 10, "nested_y": 20, "b": 2},
            ),
            (
                {"level1": {"level2": {"level3": "value"}}, "simple": "value2"},
                {"sep": "-"},
                {"level1-level2": {"level3": "value"}, "simple": "value2"},
            ),
        ],
        ids=["simple", "nested", "custom_separator"],
    )
    def test_flatten_dict_to_one_level(
        self,
        mock_mt5_import: ModuleType,
        input_dict: dict[str, Any],
        kwargs: dict[str, Any],
        expected: dict[str, Any],
    ) -> None:
        """Test _flatten_dict_to_one_level with various input structures."""
        client = Mt5DataClient(mt5=mock_mt5_import)
        result = client._flatten_dict_to_one_level(  # type: ignore[reportPrivateUsage]
            input_dict, **kwargs
        )
        assert result == expected

    @pytest.mark.parametrize(
        ("skip_to_datetime", "index_keys", "time_type", "expected_index_name"),
        [
            pytest.param(True, None, (int, np.integer), None, id="skip-to-datetime"),
            pytest.param(
                False, "name", pd.Timestamp, "name", id="convert-with-index-keys"
            ),
        ],
    )
    def test_symbols_get_as_df_with_params(
        self,
        mock_mt5_import: ModuleType,
        skip_to_datetime: bool,
        index_keys: str | None,
        time_type: type | tuple[type, ...],
        expected_index_name: str | None,
    ) -> None:
        """Test symbols_get_as_df with skip_to_datetime and index_keys parameters."""
        mock_mt5_import.symbols_get.return_value = [_MockSymbolRow()]
        client = create_initialized_client(mock_mt5_import)

        result = client.symbols_get_as_df(
            skip_to_datetime=skip_to_datetime, index_keys=index_keys
        )
        assert isinstance(result["time"].iloc[0], time_type)
        assert result.index.name == expected_index_name
        if expected_index_name is not None:
            assert "EURUSD" in result.index

    def test_symbols_get_methods_honor_positional_skip_and_index_args(
        self, mock_mt5_import: ModuleType
    ) -> None:
        """Test positional skip_to_datetime and index_keys arguments are honored."""

        class MockSymbol:
            def _asdict(self) -> dict[str, Any]:
                return {
                    "name": "EURUSD",
                    "time": 1640995200,
                    "bid": 1.1300,
                    "ask": 1.1301,
                }

        mock_mt5_import.symbols_get.return_value = [MockSymbol()]
        client = create_initialized_client(mock_mt5_import)

        dict_result = client.symbols_get_as_dicts(None, True)  # noqa: FBT003
        assert isinstance(dict_result[0]["time"], int)

        df_result = client.symbols_get_as_df(None, False, "name")  # noqa: FBT003
        assert df_result.index.name == "name"
        assert isinstance(df_result["time"].iloc[0], pd.Timestamp)

    @pytest.mark.parametrize(
        ("client_method", "mt5_method", "row", "skip_to_datetime", "time_type"),
        [
            pytest.param(
                "symbol_info_as_dict",
                "symbol_info",
                _MockSymbolRow(),
                True,
                int,
                id="symbol_info-skip",
            ),
            pytest.param(
                "symbol_info_as_dict",
                "symbol_info",
                _MockSymbolRow(),
                False,
                pd.Timestamp,
                id="symbol_info-convert",
            ),
            pytest.param(
                "symbol_info_tick_as_dict",
                "symbol_info_tick",
                MockTick(
                    time=1640995200,
                    bid=1.1300,
                    ask=1.1301,
                    last=0,
                    volume=0,
                    time_msc=1640995200000,
                    flags=0,
                    volume_real=0,
                ),
                True,
                int,
                id="symbol_info_tick-skip",
            ),
            pytest.param(
                "symbol_info_tick_as_dict",
                "symbol_info_tick",
                MockTick(
                    time=1640995200,
                    bid=1.1300,
                    ask=1.1301,
                    last=0,
                    volume=0,
                    time_msc=1640995200000,
                    flags=0,
                    volume_real=0,
                ),
                False,
                pd.Timestamp,
                id="symbol_info_tick-convert",
            ),
        ],
    )
    def test_symbol_info_dict_methods_with_skip_to_datetime(
        self,
        mock_mt5_import: ModuleType,
        client_method: str,
        mt5_method: str,
        row: object,
        skip_to_datetime: bool,
        time_type: type,
    ) -> None:
        """Test symbol_info_as_dict/symbol_info_tick_as_dict with skip_to_datetime."""
        getattr(mock_mt5_import, mt5_method).return_value = row
        client = create_initialized_client(mock_mt5_import)

        result = getattr(client, client_method)(
            "EURUSD", skip_to_datetime=skip_to_datetime
        )
        assert isinstance(result["time"], time_type)
        if time_type is int:
            assert result["time"] == 1640995200
        assert "time_msc" in result

    @pytest.mark.parametrize("skip_to_datetime", [True, False], ids=["skip", "convert"])
    def test_market_book_get_as_dicts(
        self, mock_mt5_import: ModuleType, skip_to_datetime: bool
    ) -> None:
        """Test market_book_get_as_dicts with skip_to_datetime True and default."""
        mock_book_entry = MockBookInfo(
            type=0,
            price=1.1300,
            volume=100.0,
            volume_real=100.0,
        )
        mock_mt5_import.market_book_get.return_value = [mock_book_entry]
        client = create_initialized_client(mock_mt5_import)

        result = client.market_book_get_as_dicts(
            "EURUSD", skip_to_datetime=skip_to_datetime
        )
        assert len(result) == 1
        assert result[0]["price"] == pytest.approx(1.1300)
        assert result[0]["type"] == 0

    @pytest.mark.parametrize(
        ("mt5_method", "client_method", "args"),
        [
            (
                "copy_rates_from",
                "copy_rates_from_as_dicts",
                ("EURUSD", 16385, datetime(2023, 1, 1, tzinfo=UTC), 10),
            ),
            (
                "copy_rates_from_pos",
                "copy_rates_from_pos_as_dicts",
                ("EURUSD", 16385, 0, 10),
            ),
            (
                "copy_rates_range",
                "copy_rates_range_as_dicts",
                (
                    "EURUSD",
                    16385,
                    datetime(2023, 1, 1, tzinfo=UTC),
                    datetime(2023, 1, 2, tzinfo=UTC),
                ),
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("skip_to_datetime", "time_type"),
        [
            pytest.param(True, int, id="skip"),
            pytest.param(False, pd.Timestamp, id="convert"),
        ],
    )
    def test_copy_rates_as_dicts(
        self,
        mock_mt5_import: ModuleType,
        skip_to_datetime: bool,
        time_type: type,
        mt5_method: str,
        client_method: str,
        args: tuple[object, ...],
    ) -> None:
        """Test copy_rates_*_as_dicts with skip_to_datetime True and default."""
        rate_dtype = np.dtype([
            ("time", "int64"),
            ("open", "float64"),
            ("high", "float64"),
            ("low", "float64"),
            ("close", "float64"),
        ])
        mock_rates = np.array(
            [(1640995200, 1.1300, 1.1350, 1.1280, 1.1320)],
            dtype=rate_dtype,
        )
        getattr(mock_mt5_import, mt5_method).return_value = mock_rates
        client = create_initialized_client(mock_mt5_import)

        result = getattr(client, client_method)(
            *args, skip_to_datetime=skip_to_datetime
        )
        assert len(result) == 1
        assert isinstance(result[0]["time"], time_type)
        if time_type is int:
            assert result[0]["time"] == 1640995200

    @pytest.mark.parametrize(
        ("mt5_method", "client_method", "args"),
        [
            (
                "copy_ticks_from",
                "copy_ticks_from_as_dicts",
                ("EURUSD", datetime(2023, 1, 1, tzinfo=UTC), 10, 0),
            ),
            (
                "copy_ticks_range",
                "copy_ticks_range_as_dicts",
                (
                    "EURUSD",
                    datetime(2023, 1, 1, tzinfo=UTC),
                    datetime(2023, 1, 2, tzinfo=UTC),
                    0,
                ),
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("skip_to_datetime", "time_type"),
        [
            pytest.param(True, int, id="skip"),
            pytest.param(False, pd.Timestamp, id="convert"),
        ],
    )
    def test_copy_ticks_as_dicts(
        self,
        mock_mt5_import: ModuleType,
        skip_to_datetime: bool,
        time_type: type,
        mt5_method: str,
        client_method: str,
        args: tuple[object, ...],
    ) -> None:
        """Test copy_ticks_*_as_dicts with skip_to_datetime True and default."""
        tick_dtype = np.dtype([
            ("time", "int64"),
            ("bid", "float64"),
            ("ask", "float64"),
            ("last", "float64"),
            ("volume", "uint64"),
            ("time_msc", "int64"),
            ("flags", "uint32"),
            ("volume_real", "float64"),
        ])
        mock_ticks = np.array(
            [(1640995200, 1.1300, 1.1301, 0, 0, 1640995200000, 0, 0)],
            dtype=tick_dtype,
        )
        getattr(mock_mt5_import, mt5_method).return_value = mock_ticks
        client = create_initialized_client(mock_mt5_import)

        result = getattr(client, client_method)(
            *args, skip_to_datetime=skip_to_datetime
        )
        assert len(result) == 1
        assert isinstance(result[0]["time"], time_type)
        if time_type is int:
            assert result[0]["time"] == 1640995200
        assert "time_msc" in result[0]

    @pytest.mark.parametrize(
        (
            "client_method",
            "mt5_method",
            "row",
            "call_kwargs",
            "identity",
            "time_keys",
        ),
        [
            pytest.param(
                "symbols_get_as_dicts",
                "symbols_get",
                _MockSymbolRow(),
                {},
                ("name", "EURUSD"),
                ("time", "time_msc"),
                id="symbols",
            ),
            pytest.param(
                "orders_get_as_dicts",
                "orders_get",
                MockOrder(
                    ticket=12345,
                    time_setup=1640995200,
                    time_setup_msc=1640995200000,
                    time_done=0,
                    time_done_msc=0,
                    time_expiration=1640995200,
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
                {},
                ("ticket", 12345),
                ("time_setup", "time_setup_msc"),
                id="orders",
            ),
            pytest.param(
                "positions_get_as_dicts",
                "positions_get",
                MockPosition(
                    ticket=12345,
                    time=1640995200,
                    time_msc=1640995200000,
                    time_update=1640995200,
                    time_update_msc=1640995200000,
                    type=0,
                    magic=0,
                    identifier=0,
                    reason=0,
                    volume=0.1,
                    price_open=1.1300,
                    sl=1.1200,
                    tp=1.1400,
                    price_current=1.1301,
                    swap=0.0,
                    profit=0.0,
                    symbol="EURUSD",
                    comment="",
                    external_id="",
                ),
                {},
                ("ticket", 12345),
                ("time", "time_msc"),
                id="positions",
            ),
            pytest.param(
                "history_orders_get_as_dicts",
                "history_orders_get",
                MockOrder(
                    ticket=12345,
                    time_setup=1640995200,
                    time_setup_msc=1640995200000,
                    time_done=1640995200,
                    time_done_msc=1640995200000,
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
                {
                    "date_from": datetime(2023, 1, 1, tzinfo=UTC),
                    "date_to": datetime(2023, 1, 2, tzinfo=UTC),
                },
                ("ticket", 12345),
                ("time_setup", "time_done_msc"),
                id="history_orders",
            ),
            pytest.param(
                "history_deals_get_as_dicts",
                "history_deals_get",
                MockDeal(
                    ticket=12345,
                    order=0,
                    time=1640995200,
                    time_msc=1640995200000,
                    type=0,
                    entry=0,
                    magic=0,
                    position_id=0,
                    reason=0,
                    volume=0.1,
                    price=1.1300,
                    commission=0.0,
                    swap=0.0,
                    profit=0.0,
                    fee=0.0,
                    symbol="EURUSD",
                    comment="",
                    external_id="",
                ),
                {
                    "date_from": datetime(2023, 1, 1, tzinfo=UTC),
                    "date_to": datetime(2023, 1, 2, tzinfo=UTC),
                },
                ("ticket", 12345),
                ("time", "time_msc"),
                id="history_deals",
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("skip_to_datetime", "time_type"),
        [
            pytest.param(True, int, id="skip"),
            pytest.param(False, pd.Timestamp, id="convert"),
        ],
    )
    def test_get_as_dicts_skip_to_datetime(
        self,
        mock_mt5_import: ModuleType,
        skip_to_datetime: bool,
        time_type: type,
        client_method: str,
        mt5_method: str,
        row: object,
        call_kwargs: dict[str, Any],
        identity: tuple[str, object],
        time_keys: tuple[str, str],
    ) -> None:
        """Test *_as_dicts methods with skip_to_datetime True and default conversion."""
        getattr(mock_mt5_import, mt5_method).return_value = [row]
        client = create_initialized_client(mock_mt5_import)
        identity_key, identity_value = identity
        time_key, extra_time_key = time_keys

        result = getattr(client, client_method)(
            **call_kwargs, skip_to_datetime=skip_to_datetime
        )
        assert len(result) == 1
        assert result[0][identity_key] == identity_value
        assert isinstance(result[0][time_key], time_type)
        assert extra_time_key in result[0]

    @pytest.mark.parametrize(
        (
            "client_method",
            "mt5_method",
            "call_args",
            "mock_data",
            "index_keys",
            "expected_index_value",
        ),
        [
            pytest.param(
                "copy_rates_from_as_df",
                "copy_rates_from",
                ("EURUSD", 16385, datetime(2023, 1, 1, tzinfo=UTC), 10),
                np.array(
                    [(1640995200, 1.1300, 1.1350, 1.1280, 1.1320)],
                    dtype=np.dtype([
                        ("time", "int64"),
                        ("open", "float64"),
                        ("high", "float64"),
                        ("low", "float64"),
                        ("close", "float64"),
                    ]),
                ),
                "time",
                pd.to_datetime(1640995200, unit="s"),
                id="copy_rates_from",
            ),
            pytest.param(
                "copy_ticks_from_as_df",
                "copy_ticks_from",
                ("EURUSD", datetime(2023, 1, 1, tzinfo=UTC), 10, 0),
                np.array(
                    [(1640995200, 1.1300, 1.1301, 0, 0, 1640995200000, 0, 0)],
                    dtype=np.dtype([
                        ("time", "int64"),
                        ("bid", "float64"),
                        ("ask", "float64"),
                        ("last", "float64"),
                        ("volume", "uint64"),
                        ("time_msc", "int64"),
                        ("flags", "uint32"),
                        ("volume_real", "float64"),
                    ]),
                ),
                "time_msc",
                pd.to_datetime(1640995200000, unit="ms"),
                id="copy_ticks_from",
            ),
        ],
    )
    def test_copy_methods_with_index_keys(
        self,
        mock_mt5_import: ModuleType,
        client_method: str,
        mt5_method: str,
        call_args: tuple[Any, ...],
        mock_data: np.ndarray[Any, np.dtype[Any]],
        index_keys: str,
        expected_index_value: pd.Timestamp,
    ) -> None:
        """Test copy_rates_from_as_df/copy_ticks_from_as_df with index_keys."""
        client = create_initialized_client(mock_mt5_import)
        getattr(mock_mt5_import, mt5_method).return_value = mock_data

        result = getattr(client, client_method)(*call_args, index_keys=index_keys)
        assert result.index.name == index_keys
        assert expected_index_value in result.index

    @pytest.mark.parametrize(
        ("client_method", "mt5_method", "row", "expected_index_value"),
        [
            pytest.param(
                "orders_get_as_df",
                "orders_get",
                MockOrder(
                    ticket=12345,
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
                12345,
                id="orders_get",
            ),
            pytest.param(
                "positions_get_as_df",
                "positions_get",
                MockPosition(
                    ticket=54321,
                    time=1640995200,
                    time_msc=1640995200000,
                    time_update=1640995200,
                    time_update_msc=1640995200000,
                    type=0,
                    magic=0,
                    identifier=0,
                    reason=0,
                    volume=0.1,
                    price_open=1.1300,
                    sl=1.1200,
                    tp=1.1400,
                    price_current=1.1301,
                    swap=0.0,
                    profit=0.0,
                    symbol="EURUSD",
                    comment="",
                    external_id="",
                ),
                54321,
                id="positions_get",
            ),
        ],
    )
    def test_orders_positions_get_as_df_with_index_keys(
        self,
        mock_mt5_import: ModuleType,
        client_method: str,
        mt5_method: str,
        row: object,
        expected_index_value: int,
    ) -> None:
        """Test orders_get_as_df/positions_get_as_df with index_keys='ticket'."""
        client = create_initialized_client(mock_mt5_import)
        getattr(mock_mt5_import, mt5_method).return_value = [row]

        result = getattr(client, client_method)(index_keys="ticket")
        assert result.index.name == "ticket"
        assert expected_index_value in result.index

    def test_orders_get_as_df_empty_result_has_no_index(
        self, mock_mt5_import: ModuleType
    ) -> None:
        """Test orders_get_as_df doesn't set an index on an empty DataFrame."""
        client = create_initialized_client(mock_mt5_import)
        mock_mt5_import.orders_get.return_value = []

        result = client.orders_get_as_df(index_keys="ticket")
        assert result.empty
        assert result.index.name is None

    def test_set_index_if_possible_decorator(self, mock_mt5_import: ModuleType) -> None:
        """Test set_index_if_possible decorator does not set index when unrequested.

        The empty-DataFrame-with-index_keys branch is covered by
        test_orders_get_as_df_empty_result_has_no_index.
        """
        client = Mt5DataClient(mt5=mock_mt5_import)

        # Mock symbol data
        class MockSymbol:
            def _asdict(self) -> dict[str, Any]:
                return {
                    "name": "EURUSD",
                    "time": 1640995200,
                    "bid": 1.1300,
                    "ask": 1.1301,
                }

        mock_mt5_import.symbols_get.return_value = [MockSymbol()]
        mock_mt5_import.initialize.return_value = True

        client.initialize()

        # Test with index_keys=None (should not set index)
        result = client.symbols_get_as_df(index_keys=None)
        assert result.index.name is None

    def test_detect_and_convert_time_decorator_non_dict_object(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test detect_and_convert_time decorator with non-dict return value."""
        # Mock a method that returns a non-dict, non-list, non-DataFrame object
        mock_mt5_import.symbols_total.return_value = 42
        client = create_initialized_client(mock_mt5_import)

        # This should trigger the else path
        result = client.symbols_total()
        assert result == 42  # Should return unchanged

    def test_convert_time_decorator_non_standard_return_type(
        self,
        mock_mt5_import: ModuleType,
    ) -> None:
        """Test detect_and_convert_time decorator with non-standard return type."""
        # This test specifically targets return result (else case)

        # Mock a method that returns a string (not dict, list, or DataFrame)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.version.return_value = (123, 456, "2024-01-01")  # returns tuple

        client = create_initialized_client(mock_mt5_import)

        # version() returns a tuple, which should trigger the else clause
        result = client.version()
        assert isinstance(result, tuple)
        assert result == (123, 456, "2024-01-01")  # Should return unchanged

    def test_convert_time_decorator_string_return_type(self) -> None:
        """Test detect_and_convert_time decorator with string return type."""
        # This test specifically targets return result (else case)

        @detect_and_convert_time_to_datetime(skip_toggle="skip_to_datetime")
        def mock_function_returning_string(skip_to_datetime: bool = False) -> str:  # noqa: ARG001
            """Mock function that returns a string."""
            return "test_string"  # Return string instead of dict/list/DataFrame

        # Call with skip_to_datetime=False (should trigger else clause)
        result = mock_function_returning_string(skip_to_datetime=False)
        assert result == "test_string"  # Should return unchanged

        # Call with skip_to_datetime=True (should trigger early return)
        result = mock_function_returning_string(skip_to_datetime=True)
        assert result == "test_string"  # Should return unchanged
