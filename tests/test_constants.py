"""Tests for pdmt5.constants module."""

import importlib
import sys
from collections.abc import Callable, Mapping
from types import ModuleType
from typing import cast

import pytest

import pdmt5
from pdmt5.constants import (
    COPY_TICKS_MAP,
    ORDER_TYPE_MAP,
    TIMEFRAME_MAP,
    get_copy_ticks_name,
    get_copy_ticks_value,
    get_order_type_name,
    get_order_type_value,
    get_timeframe_name,
    get_timeframe_value,
    list_copy_ticks_names,
    list_copy_ticks_values,
    list_order_type_names,
    list_order_type_values,
    list_timeframe_names,
    list_timeframe_values,
    parse_copy_ticks,
    parse_order_type,
    parse_timeframe,
)

_WINDOWS_ONLY = pytest.mark.skipif(
    sys.platform != "win32",
    reason="MetaTrader5 Python package is available only on Windows.",
)


@pytest.fixture(scope="module")
def real_mt5_module() -> ModuleType:
    """Import the real MetaTrader5 Python package for Windows parity tests."""
    return importlib.import_module("MetaTrader5")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("TIMEFRAME_M1", 1),
        ("M1", 1),
        ("timeframe_h1", 16385),
        ("h1", 16385),
        ("  TIMEFRAME_MN1  ", 49153),
        ("49153", 49153),
        (16408, 16408),
    ],
)
def test_parse_timeframe_accepts_official_names_aliases_and_values(
    value: int | str,
    expected: int,
) -> None:
    """Test timeframe parsing for supported input forms."""
    assert parse_timeframe(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("COPY_TICKS_ALL", -1),
        ("ALL", -1),
        ("copy_ticks_info", 1),
        ("trade", 2),
        ("2", 2),
        (1, 1),
    ],
)
def test_parse_copy_ticks_accepts_official_names_aliases_and_values(
    value: int | str,
    expected: int,
) -> None:
    """Test COPY_TICKS parsing for supported input forms."""
    assert parse_copy_ticks(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("ORDER_TYPE_BUY", 0),
        ("BUY", 0),
        ("order_type_sell_limit", 3),
        ("sell_stop_limit", 7),
        ("8", 8),
        (5, 5),
    ],
)
def test_parse_order_type_accepts_official_names_aliases_and_values(
    value: int | str,
    expected: int,
) -> None:
    """Test ORDER_TYPE parsing for supported input forms."""
    assert parse_order_type(value) == expected


@pytest.mark.parametrize(
    ("parser", "value", "match"),
    [
        (parse_timeframe, "M7", "Invalid MT5 timeframe"),
        (parse_timeframe, 8, "Unsupported MT5 timeframe value"),
        (parse_timeframe, True, "Invalid MT5 timeframe"),
        (parse_timeframe, 1.0, "Invalid MT5 timeframe"),
        (parse_timeframe, None, "Invalid MT5 timeframe"),
        (parse_timeframe, object(), "Invalid MT5 timeframe"),
        (parse_copy_ticks, "QUOTE", "Invalid MT5 COPY_TICKS flag"),
        (parse_copy_ticks, 4, "Unsupported MT5 COPY_TICKS flag value"),
        (parse_copy_ticks, False, "Invalid MT5 COPY_TICKS flag"),
        (parse_copy_ticks, 1.0, "Invalid MT5 COPY_TICKS flag"),
        (parse_order_type, "MARKET_BUY", "Invalid MT5 ORDER_TYPE"),
        (parse_order_type, 9, "Unsupported MT5 ORDER_TYPE value"),
        (parse_order_type, True, "Invalid MT5 ORDER_TYPE"),
        (parse_order_type, 1.0, "Invalid MT5 ORDER_TYPE"),
    ],
)
def test_parse_constants_reject_invalid_inputs(
    parser: Callable[[object], int],
    value: object,
    match: str,
) -> None:
    """Test invalid names, invalid integers, and bool values are rejected."""
    with pytest.raises(ValueError, match=match):
        parser(value)


def test_timeframe_helpers_return_schema_friendly_names_and_values() -> None:
    """Test timeframe helper names and values for JSON schemas."""
    assert TIMEFRAME_MAP["TIMEFRAME_M1"] == 1
    assert TIMEFRAME_MAP["M1"] == 1
    assert list_timeframe_names(include_aliases=False) == [
        "TIMEFRAME_M1",
        "TIMEFRAME_M2",
        "TIMEFRAME_M3",
        "TIMEFRAME_M4",
        "TIMEFRAME_M5",
        "TIMEFRAME_M6",
        "TIMEFRAME_M10",
        "TIMEFRAME_M12",
        "TIMEFRAME_M15",
        "TIMEFRAME_M20",
        "TIMEFRAME_M30",
        "TIMEFRAME_H1",
        "TIMEFRAME_H2",
        "TIMEFRAME_H3",
        "TIMEFRAME_H4",
        "TIMEFRAME_H6",
        "TIMEFRAME_H8",
        "TIMEFRAME_H12",
        "TIMEFRAME_D1",
        "TIMEFRAME_W1",
        "TIMEFRAME_MN1",
    ]
    assert "M1" in list_timeframe_names()
    assert list_timeframe_values() == [
        1,
        2,
        3,
        4,
        5,
        6,
        10,
        12,
        15,
        20,
        30,
        16385,
        16386,
        16387,
        16388,
        16390,
        16392,
        16396,
        16408,
        32769,
        49153,
    ]
    assert get_timeframe_value("TIMEFRAME_H4") == 16388
    assert get_timeframe_name(16388) == "TIMEFRAME_H4"
    assert get_timeframe_name(16388, prefer_alias=True) == "H4"


def test_copy_ticks_helpers_return_schema_friendly_names_and_values() -> None:
    """Test COPY_TICKS helper names and values for JSON schemas."""
    assert COPY_TICKS_MAP["COPY_TICKS_ALL"] == -1
    assert COPY_TICKS_MAP["ALL"] == -1
    assert list_copy_ticks_names(include_aliases=False) == [
        "COPY_TICKS_INFO",
        "COPY_TICKS_TRADE",
        "COPY_TICKS_ALL",
    ]
    assert "ALL" in list_copy_ticks_names()
    assert list_copy_ticks_values() == [1, 2, -1]
    assert get_copy_ticks_value("COPY_TICKS_TRADE") == 2
    assert get_copy_ticks_name(2) == "COPY_TICKS_TRADE"
    assert get_copy_ticks_name(2, prefer_alias=True) == "TRADE"


def test_order_type_helpers_return_schema_friendly_names_and_values() -> None:
    """Test ORDER_TYPE helper names and values for JSON schemas."""
    assert ORDER_TYPE_MAP["ORDER_TYPE_BUY"] == 0
    assert ORDER_TYPE_MAP["BUY"] == 0
    assert list_order_type_names(include_aliases=False) == [
        "ORDER_TYPE_BUY",
        "ORDER_TYPE_SELL",
        "ORDER_TYPE_BUY_LIMIT",
        "ORDER_TYPE_SELL_LIMIT",
        "ORDER_TYPE_BUY_STOP",
        "ORDER_TYPE_SELL_STOP",
        "ORDER_TYPE_BUY_STOP_LIMIT",
        "ORDER_TYPE_SELL_STOP_LIMIT",
        "ORDER_TYPE_CLOSE_BY",
    ]
    assert "BUY" in list_order_type_names()
    assert list_order_type_values() == [0, 1, 2, 3, 4, 5, 6, 7, 8]
    assert get_order_type_value("ORDER_TYPE_SELL_STOP") == 5
    assert get_order_type_name(5) == "ORDER_TYPE_SELL_STOP"
    assert get_order_type_name(5, prefer_alias=True) == "SELL_STOP"


@pytest.mark.parametrize(
    ("getter", "value"),
    [
        (get_timeframe_name, 7),
        (get_copy_ticks_name, 4),
        (get_order_type_name, 9),
    ],
)
def test_name_helpers_reject_invalid_values(
    getter: Callable[[int], str],
    value: int,
) -> None:
    """Test name lookup helpers reject invalid integer constants."""
    with pytest.raises(ValueError, match="Unsupported MT5"):
        getter(value)


@pytest.mark.parametrize(
    ("constant_map", "key", "bad_value", "parser", "parser_value", "expected"),
    [
        (TIMEFRAME_MAP, "M1", 999, parse_timeframe, "M1", 1),
        (COPY_TICKS_MAP, "ALL", 999, parse_copy_ticks, "ALL", -1),
        (ORDER_TYPE_MAP, "BUY", 999, parse_order_type, "BUY", 0),
    ],
)
def test_public_constant_maps_are_immutable_and_do_not_affect_parsers(
    constant_map: Mapping[str, int],
    key: str,
    bad_value: int,
    parser: Callable[[object], int],
    parser_value: str,
    expected: int,
) -> None:
    """Test exported maps cannot be mutated to change parser behavior."""
    mutable_view = cast("dict[str, int]", constant_map)
    with pytest.raises(TypeError):
        mutable_view[key] = bad_value

    assert parser(parser_value) == expected


@pytest.mark.parametrize(
    "export",
    [
        "COPY_TICKS_MAP",
        "ORDER_TYPE_MAP",
        "TIMEFRAME_MAP",
        "get_copy_ticks_name",
        "get_copy_ticks_value",
        "get_order_type_name",
        "get_order_type_value",
        "get_timeframe_name",
        "get_timeframe_value",
        "list_copy_ticks_names",
        "list_copy_ticks_values",
        "list_order_type_names",
        "list_order_type_values",
        "list_timeframe_names",
        "list_timeframe_values",
        "parse_copy_ticks",
        "parse_order_type",
        "parse_timeframe",
    ],
)
def test_constants_exports_available(export: str) -> None:
    """Test new public constants APIs are exported by pdmt5."""
    assert hasattr(pdmt5, export), f"Missing export: {export}"
    assert export in pdmt5.__all__, f"Export {export} not in __all__"


@_WINDOWS_ONLY
@pytest.mark.parametrize("name", list_timeframe_names(include_aliases=False))
def test_timeframe_constants_match_metatrader5_package(
    real_mt5_module: ModuleType,
    name: str,
) -> None:
    """Test pdmt5 timeframe constants match the real MetaTrader5 package."""
    assert TIMEFRAME_MAP[name] == int(getattr(real_mt5_module, name))


@_WINDOWS_ONLY
@pytest.mark.parametrize("name", list_copy_ticks_names(include_aliases=False))
def test_copy_ticks_constants_match_metatrader5_package(
    real_mt5_module: ModuleType,
    name: str,
) -> None:
    """Test pdmt5 COPY_TICKS constants match the real MetaTrader5 package."""
    assert COPY_TICKS_MAP[name] == int(getattr(real_mt5_module, name))


@_WINDOWS_ONLY
@pytest.mark.parametrize("name", list_order_type_names(include_aliases=False))
def test_order_type_constants_match_metatrader5_package(
    real_mt5_module: ModuleType,
    name: str,
) -> None:
    """Test pdmt5 ORDER_TYPE constants match the real MetaTrader5 package."""
    assert ORDER_TYPE_MAP[name] == int(getattr(real_mt5_module, name))
