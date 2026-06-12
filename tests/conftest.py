"""Shared pytest helpers."""

from collections.abc import Iterable, Mapping
from types import ModuleType
from typing import Any, cast

from pytest_mock import MockerFixture


def create_mock_mt5_module(
    mocker: MockerFixture,
    *,
    methods: Iterable[str],
    constants: Mapping[str, object] | None = None,
) -> ModuleType:
    """Create a ModuleType-backed MetaTrader5 mock."""
    mock_mt5 = ModuleType("mock_mt5")
    mock_mt5_any = cast("Any", mock_mt5)

    magic_mock = mocker.MagicMock()
    for attr in dir(magic_mock):
        if not attr.startswith("__") or attr == "__call__":
            setattr(mock_mt5_any, attr, getattr(magic_mock, attr))

    for method in methods:
        setattr(mock_mt5_any, method, mocker.MagicMock())

    for name, value in (constants or {}).items():
        setattr(mock_mt5_any, name, value)

    return mock_mt5
