"""Focused tests for config-aware MetaTrader5 initialization."""

from types import ModuleType, SimpleNamespace
from typing import Any, cast

import pytest
from pytest_mock import MockerFixture

from pdmt5.dataframe import Mt5Config, Mt5DataClient
from tests.helpers import create_mock_mt5_module

_MT5_METHODS = ("initialize", "login", "account_info", "last_error", "shutdown")


def _make_client(mocker: MockerFixture) -> tuple[ModuleType, Mt5DataClient]:
    mt5 = create_mock_mt5_module(
        mocker,
        methods=_MT5_METHODS,
        constants={"RES_S_OK": 1},
    )
    mt5_any = cast("Any", mt5)
    mt5_any.initialize.return_value = True
    mt5_any.login.return_value = True
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


@pytest.mark.parametrize(
    ("active_account", "should_login"),
    [
        pytest.param(
            SimpleNamespace(login=123456, server="Demo"),
            False,
            id="matching-account",
        ),
        pytest.param(
            SimpleNamespace(login=654321, server="Demo"),
            True,
            id="different-login",
        ),
        pytest.param(
            SimpleNamespace(login=123456, server="Other"),
            True,
            id="different-server",
        ),
        pytest.param(None, True, id="account-info-unavailable"),
    ],
)
def test_initialize_uses_explicit_login_only_when_requested_account_is_not_active(
    mocker: MockerFixture,
    active_account: SimpleNamespace | None,
    *,
    should_login: bool,
) -> None:
    """Skip only when both the requested login and server are already active."""
    mt5, client = _make_client(mocker)
    mt5_any = cast("Any", mt5)
    mt5_any.account_info.return_value = active_account

    client.initialize_and_login_mt5()

    mt5_any.account_info.assert_called_once()
    if should_login:
        mt5_any.login.assert_called_once_with(
            123456,
            password="secret",
            server="Demo",
            timeout=60000,
        )
    else:
        mt5_any.login.assert_not_called()
