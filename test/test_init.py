"""Tests for pdmt5 package initialization."""

import pdmt5


class TestInit:
    """Test package initialization."""

    def test_version_attribute(self) -> None:
        """Test that __version__ attribute exists."""
        assert hasattr(pdmt5, "__version__")
        assert pdmt5.__version__ is not None

    def test_all_exports(self) -> None:
        """Test that all expected exports are available."""
        expected_exports = [
            "DealEntry",
            "DealReason",
            "DealType",
            "Mt5Config",
            "Mt5DataClient",
            "Mt5RuntimeError",
            "OrderFilling",
            "OrderState",
            "OrderTime",
            "OrderType",
            "PositionType",
            "SymbolCalcMode",
            "SymbolExpiration",
            "SymbolFillMode",
            "SymbolOption",
            "SymbolOptionRight",
            "SymbolOrderMode",
            "SymbolSwapMode",
            "SymbolTradeMode",
            "TickFlag",
            "Timeframe",
            "TradeAction",
        ]

        for export in expected_exports:
            assert hasattr(pdmt5, export), f"Missing export: {export}"
            assert export in pdmt5.__all__, f"Export {export} not in __all__"

    def test_constants_accessible(self) -> None:
        """Test that constants are accessible."""
        assert hasattr(pdmt5, "Timeframe")
        assert hasattr(pdmt5, "TickFlag")
        assert hasattr(pdmt5, "OrderType")

    def test_classes_accessible(self) -> None:
        """Test that main classes are accessible."""
        assert hasattr(pdmt5, "Mt5Config")
        assert hasattr(pdmt5, "Mt5DataClient")
        assert hasattr(pdmt5, "Mt5RuntimeError")
