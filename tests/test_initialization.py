"""Focused tests for config-aware MetaTrader5 initialization."""

from types import SimpleNamespace

from pytest_mock import MockerFixture

from pdmt5.dataframe import Mt5Config, Mt5DataClient
from tests.helpers import create_mock_mt5_module

_MT5_METHODS = ("initialize", "login", "account_info", "last_error", "shutdown")


def _make_client(mocker: MockerFixture, *, active_login: int) -> tuple[object, Mt5DataClient]:
    mt5 = create_mock_mt5_module(
        mocker,
        methods=_MT5_METHODS,
        constants={"RES_S_OK": 1},
    )
    mt5.initialize.return_value = True  # type: ignore[attr-defined]
    mt5.login.return_value = True  # type: ignore[attr-defined]
    mt5.account_info.return_value = SimpleNamespace(login=active_login)  # type: ignore[attr-defined]
    mt5.last_error.return_value = (1, "Success")  # type: ignore[attr-defined]
    client = Mt5DataClient(
        mt5=mt5,
        config=Mt5Config(
            login=123456,
            password="secret",
            server="Demo",
            timeout=60000,
        ),
        retry_count=0,
    )
    return mt5, client


def test_initialize_skips_redundant_login_for_active_account(
    mocker: MockerFixture,
) -> None:
    """Do not authenticate twice when initialize already selected the account."""
    mt5, client = _make_client(mocker, active_login=123456)

    client.initialize_and_login_mt5()

    mt5.account_info.assert_called_once()  # type: ignore[attr-defined]
    mt5.login.assert_not_called()  # type: ignore[attr-defined]


def test_initialize_falls_back_to_login_for_different_active_account(
    mocker: MockerFixture,
) -> None:
    """Preserve explicit login fallback when initialize leaves another account active."""
    mt5, client = _make_client(mocker, active_login=654321)

    client.initialize_and_login_mt5()

    mt5.account_info.assert_called_once()  # type: ignore[attr-defined]
    mt5.login.assert_called_once_with(  # type: ignore[attr-defined]
        123456,
        password="secret",
        server="Demo",
        timeout=60000,
    )
