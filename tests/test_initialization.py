"""Focused tests for config-aware MetaTrader5 initialization."""

from types import ModuleType, SimpleNamespace
from typing import Any, cast

from pytest_mock import MockerFixture

from pdmt5.dataframe import Mt5Config, Mt5DataClient
from tests.helpers import create_mock_mt5_module

_MT5_METHODS = ("initialize", "login", "account_info", "last_error", "shutdown")


def _make_client(
    mocker: MockerFixture,
    *,
    active_login: int,
) -> tuple[ModuleType, Mt5DataClient]:
    mt5 = create_mock_mt5_module(
        mocker,
        methods=_MT5_METHODS,
        constants={"RES_S_OK": 1},
    )
    mt5_any = cast("Any", mt5)
    mt5_any.initialize.return_value = True
    mt5_any.login.return_value = True
    mt5_any.account_info.return_value = SimpleNamespace(login=active_login)
    mt5_any.last_error.return_value = (1, "Success")
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
    mt5_any = cast("Any", mt5)

    client.initialize_and_login_mt5()

    mt5_any.account_info.assert_called_once()
    mt5_any.login.assert_not_called()


def test_initialize_falls_back_to_login_for_different_active_account(
    mocker: MockerFixture,
) -> None:
    """Use explicit login when initialize leaves another account active."""
    mt5, client = _make_client(mocker, active_login=654321)
    mt5_any = cast("Any", mt5)

    client.initialize_and_login_mt5()

    mt5_any.account_info.assert_called_once()
    mt5_any.login.assert_called_once_with(
        123456,
        password="secret",
        server="Demo",
        timeout=60000,
    )


def test_initialize_falls_back_to_login_when_account_info_is_unavailable(
    mocker: MockerFixture,
) -> None:
    """Use explicit login if active-account verification cannot return data."""
    mt5, client = _make_client(mocker, active_login=123456)
    mt5_any = cast("Any", mt5)
    mt5_any.account_info.return_value = None

    client.initialize_and_login_mt5()

    mt5_any.login.assert_called_once_with(
        123456,
        password="secret",
        server="Demo",
        timeout=60000,
    )
