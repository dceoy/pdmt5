"""Tests for pdmt5 package initialization."""

import pytest

import pdmt5

_STABLE_ROOT_EXPORTS = {
    "__version__",
    "COPY_TICKS_MAP",
    "ORDER_TYPE_MAP",
    "TIMEFRAME_MAP",
    "Mt5Client",
    "Mt5Config",
    "Mt5DataClient",
    "Mt5RuntimeError",
    "parse_copy_ticks",
    "parse_order_type",
    "parse_timeframe",
}


class TestInit:
    """Test package initialization."""

    def test_version_attribute(self) -> None:
        """Test that __version__ attribute exists."""
        assert hasattr(pdmt5, "__version__")
        assert pdmt5.__version__ is not None

    def test_stable_root_exports_match_contract(self) -> None:
        """Test that the root API is an explicit, importable allowlist."""
        assert set(pdmt5.__all__) == _STABLE_ROOT_EXPORTS
        assert all(hasattr(pdmt5, export) for export in pdmt5.__all__)

    @pytest.mark.parametrize(
        "removed_export",
        [
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
        ],
    )
    def test_compatibility_helpers_are_not_root_exports(
        self, removed_export: str
    ) -> None:
        """Test that constant introspection stays in pdmt5.constants."""
        assert not hasattr(pdmt5, removed_export)
