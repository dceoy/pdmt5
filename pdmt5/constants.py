"""MetaTrader 5 constant parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

_TIMEFRAME_ALIASES: Final[dict[str, int]] = {
    "M1": 1,
    "M2": 2,
    "M3": 3,
    "M4": 4,
    "M5": 5,
    "M6": 6,
    "M10": 10,
    "M12": 12,
    "M15": 15,
    "M20": 20,
    "M30": 30,
    "H1": 16385,
    "H2": 16386,
    "H3": 16387,
    "H4": 16388,
    "H6": 16390,
    "H8": 16392,
    "H12": 16396,
    "D1": 16408,
    "W1": 32769,
    "MN1": 49153,
}
_COPY_TICKS_ALIASES: Final[dict[str, int]] = {
    "INFO": 1,
    "TRADE": 2,
    "ALL": 3,
}
_ORDER_TYPE_ALIASES: Final[dict[str, int]] = {
    "BUY": 0,
    "SELL": 1,
    "BUY_LIMIT": 2,
    "SELL_LIMIT": 3,
    "BUY_STOP": 4,
    "SELL_STOP": 5,
    "BUY_STOP_LIMIT": 6,
    "SELL_STOP_LIMIT": 7,
    "CLOSE_BY": 8,
}

_TIMEFRAME_OFFICIAL_NAMES: Final[tuple[str, ...]] = tuple(
    f"TIMEFRAME_{name}" for name in _TIMEFRAME_ALIASES
)
_COPY_TICKS_OFFICIAL_NAMES: Final[tuple[str, ...]] = tuple(
    f"COPY_TICKS_{name}" for name in _COPY_TICKS_ALIASES
)
_ORDER_TYPE_OFFICIAL_NAMES: Final[tuple[str, ...]] = tuple(
    f"ORDER_TYPE_{name}" for name in _ORDER_TYPE_ALIASES
)

_TIMEFRAME_OFFICIAL_MAP: Final[dict[str, int]] = {
    name: value
    for name, value in zip(
        _TIMEFRAME_OFFICIAL_NAMES,
        _TIMEFRAME_ALIASES.values(),
        strict=True,
    )
}
_COPY_TICKS_OFFICIAL_MAP: Final[dict[str, int]] = {
    name: value
    for name, value in zip(
        _COPY_TICKS_OFFICIAL_NAMES,
        _COPY_TICKS_ALIASES.values(),
        strict=True,
    )
}
_ORDER_TYPE_OFFICIAL_MAP: Final[dict[str, int]] = {
    name: value
    for name, value in zip(
        _ORDER_TYPE_OFFICIAL_NAMES,
        _ORDER_TYPE_ALIASES.values(),
        strict=True,
    )
}

TIMEFRAME_MAP: Final[dict[str, int]] = {
    **_TIMEFRAME_OFFICIAL_MAP,
    **_TIMEFRAME_ALIASES,
}
COPY_TICKS_MAP: Final[dict[str, int]] = {
    **_COPY_TICKS_OFFICIAL_MAP,
    **_COPY_TICKS_ALIASES,
}
ORDER_TYPE_MAP: Final[dict[str, int]] = {
    **_ORDER_TYPE_OFFICIAL_MAP,
    **_ORDER_TYPE_ALIASES,
}


@dataclass(frozen=True)
class _ConstantFamily:
    """Metadata for one MT5 constant family."""

    label: str
    mapping: dict[str, int]
    official_names: tuple[str, ...]
    alias_names: tuple[str, ...]

    @property
    def values(self) -> list[int]:
        """Return unique constant values in official MT5 order."""
        return list(dict.fromkeys(self.mapping.values()))

    @property
    def value_set(self) -> set[int]:
        """Return unique constant values for membership checks."""
        return set(self.values)

    def names(self, *, include_aliases: bool = True) -> list[str]:
        """Return accepted constant names.

        Args:
            include_aliases: Include short aliases such as ``M1`` or ``BUY``.

        Returns:
            Accepted constant names in schema-friendly order.
        """
        names = list(self.official_names)
        if include_aliases:
            names.extend(self.alias_names)
        return names

    def name_by_value(self, value: int, *, prefer_alias: bool = False) -> str:
        """Return the name for a constant value.

        Args:
            value: Integer constant value.
            prefer_alias: Return the short alias instead of the official name.

        Returns:
            The matching constant name.

        Raises:
            ValueError: If the integer is not valid for this family.
        """
        parsed_value = _parse_constant(value, self)
        names = self.alias_names if prefer_alias else self.official_names
        value_map = {self.mapping[name]: name for name in names}
        return value_map[parsed_value]


_TIMEFRAME_FAMILY: Final[_ConstantFamily] = _ConstantFamily(
    label="MT5 timeframe",
    mapping=TIMEFRAME_MAP,
    official_names=_TIMEFRAME_OFFICIAL_NAMES,
    alias_names=tuple(_TIMEFRAME_ALIASES),
)
_COPY_TICKS_FAMILY: Final[_ConstantFamily] = _ConstantFamily(
    label="MT5 COPY_TICKS flag",
    mapping=COPY_TICKS_MAP,
    official_names=_COPY_TICKS_OFFICIAL_NAMES,
    alias_names=tuple(_COPY_TICKS_ALIASES),
)
_ORDER_TYPE_FAMILY: Final[_ConstantFamily] = _ConstantFamily(
    label="MT5 ORDER_TYPE",
    mapping=ORDER_TYPE_MAP,
    official_names=_ORDER_TYPE_OFFICIAL_NAMES,
    alias_names=tuple(_ORDER_TYPE_ALIASES),
)


def _parse_constant(value: int | str, family: _ConstantFamily) -> int:
    """Parse a constant name or value for a family."""
    if isinstance(value, str):
        normalized_value = value.strip().upper()
        if normalized_value in family.mapping:
            return family.mapping[normalized_value]
        try:
            parsed_value = int(normalized_value)
        except ValueError:
            valid_names = ", ".join(family.names())
            message = (
                f"Invalid {family.label}: {value!r}. Use one of: {valid_names}, "
                "or a valid integer value."
            )
            raise ValueError(message) from None
    elif isinstance(value, bool) or not isinstance(value, int):
        message = f"Invalid {family.label}: {value!r}. Use a name or integer value."
        raise ValueError(message)
    else:
        parsed_value = value

    if parsed_value not in family.value_set:
        valid_values = ", ".join(str(v) for v in family.values)
        message = (
            f"Unsupported {family.label} value: {parsed_value}. "
            f"Use one of: {valid_values}."
        )
        raise ValueError(message)
    return parsed_value


def parse_timeframe(value: int | str) -> int:
    """Parse a MetaTrader 5 timeframe name, alias, or integer value.

    Args:
        value: Official name (``TIMEFRAME_M1``), short alias (``M1``), or integer
            value.

    Returns:
        The validated MetaTrader 5 timeframe integer.

    Raises:
        ValueError: If the value is not valid for MT5 timeframes.
    """
    return _parse_constant(value=value, family=_TIMEFRAME_FAMILY)


def parse_copy_ticks(value: int | str) -> int:
    """Parse a MetaTrader 5 COPY_TICKS name, alias, or integer value.

    Args:
        value: Official name (``COPY_TICKS_ALL``), short alias (``ALL``), or
            integer value.

    Returns:
        The validated MetaTrader 5 COPY_TICKS integer.

    Raises:
        ValueError: If the value is not valid for MT5 COPY_TICKS flags.
    """
    return _parse_constant(value=value, family=_COPY_TICKS_FAMILY)


def parse_order_type(value: int | str) -> int:
    """Parse a MetaTrader 5 ORDER_TYPE name, alias, or integer value.

    Args:
        value: Official name (``ORDER_TYPE_BUY``), short alias (``BUY``), or
            integer value.

    Returns:
        The validated MetaTrader 5 ORDER_TYPE integer.

    Raises:
        ValueError: If the value is not valid for MT5 order types.
    """
    return _parse_constant(value=value, family=_ORDER_TYPE_FAMILY)


def list_timeframe_names(*, include_aliases: bool = True) -> list[str]:
    """Return MT5 timeframe names for JSON schema generation.

    Args:
        include_aliases: Include short aliases such as ``M1``.

    Returns:
        Accepted timeframe names.
    """
    return _TIMEFRAME_FAMILY.names(include_aliases=include_aliases)


def list_timeframe_values() -> list[int]:
    """Return valid MT5 timeframe integer values for JSON schema generation.

    Returns:
        Valid timeframe integer values.
    """
    return _TIMEFRAME_FAMILY.values


def get_timeframe_value(name: str) -> int:
    """Return the integer value for an MT5 timeframe name or alias.

    Args:
        name: Official timeframe name or short alias.

    Returns:
        The matching timeframe integer.

    Raises:
        ValueError: If the name is not valid for MT5 timeframes.
    """
    return parse_timeframe(name)


def get_timeframe_name(value: int, *, prefer_alias: bool = False) -> str:
    """Return the MT5 timeframe name for an integer value.

    Args:
        value: Timeframe integer value.
        prefer_alias: Return the short alias instead of the official name.

    Returns:
        The matching timeframe name.

    Raises:
        ValueError: If the value is not valid for MT5 timeframes.
    """
    return _TIMEFRAME_FAMILY.name_by_value(value=value, prefer_alias=prefer_alias)


def list_copy_ticks_names(*, include_aliases: bool = True) -> list[str]:
    """Return MT5 COPY_TICKS names for JSON schema generation.

    Args:
        include_aliases: Include short aliases such as ``ALL``.

    Returns:
        Accepted COPY_TICKS names.
    """
    return _COPY_TICKS_FAMILY.names(include_aliases=include_aliases)


def list_copy_ticks_values() -> list[int]:
    """Return valid MT5 COPY_TICKS integer values for JSON schema generation.

    Returns:
        Valid COPY_TICKS integer values.
    """
    return _COPY_TICKS_FAMILY.values


def get_copy_ticks_value(name: str) -> int:
    """Return the integer value for an MT5 COPY_TICKS name or alias.

    Args:
        name: Official COPY_TICKS name or short alias.

    Returns:
        The matching COPY_TICKS integer.

    Raises:
        ValueError: If the name is not valid for MT5 COPY_TICKS flags.
    """
    return parse_copy_ticks(name)


def get_copy_ticks_name(value: int, *, prefer_alias: bool = False) -> str:
    """Return the MT5 COPY_TICKS name for an integer value.

    Args:
        value: COPY_TICKS integer value.
        prefer_alias: Return the short alias instead of the official name.

    Returns:
        The matching COPY_TICKS name.

    Raises:
        ValueError: If the value is not valid for MT5 COPY_TICKS flags.
    """
    return _COPY_TICKS_FAMILY.name_by_value(value=value, prefer_alias=prefer_alias)


def list_order_type_names(*, include_aliases: bool = True) -> list[str]:
    """Return MT5 ORDER_TYPE names for JSON schema generation.

    Args:
        include_aliases: Include short aliases such as ``BUY``.

    Returns:
        Accepted ORDER_TYPE names.
    """
    return _ORDER_TYPE_FAMILY.names(include_aliases=include_aliases)


def list_order_type_values() -> list[int]:
    """Return valid MT5 ORDER_TYPE integer values for JSON schema generation.

    Returns:
        Valid ORDER_TYPE integer values.
    """
    return _ORDER_TYPE_FAMILY.values


def get_order_type_value(name: str) -> int:
    """Return the integer value for an MT5 ORDER_TYPE name or alias.

    Args:
        name: Official ORDER_TYPE name or short alias.

    Returns:
        The matching ORDER_TYPE integer.

    Raises:
        ValueError: If the name is not valid for MT5 order types.
    """
    return parse_order_type(name)


def get_order_type_name(value: int, *, prefer_alias: bool = False) -> str:
    """Return the MT5 ORDER_TYPE name for an integer value.

    Args:
        value: ORDER_TYPE integer value.
        prefer_alias: Return the short alias instead of the official name.

    Returns:
        The matching ORDER_TYPE name.

    Raises:
        ValueError: If the value is not valid for MT5 order types.
    """
    return _ORDER_TYPE_FAMILY.name_by_value(value=value, prefer_alias=prefer_alias)


__all__ = [
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
]
