"""Tests for pdmt5.report module."""

# pyright: reportPrivateUsage=false
# pyright: reportAttributeAccessIssue=false

from collections.abc import Generator
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from pdmt5.dataframe import Mt5DataClient
from pdmt5.report import Mt5ReportClient

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
        mock_mt5.last_error = mocker.MagicMock(return_value=(0, "No error"))  # type: ignore[attr-defined]
        mock_mt5.account_info = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.terminal_info = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbols_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbol_info = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_rates_from = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_ticks_from = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_rates_from_pos = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_rates_range = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.copy_ticks_range = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbol_info_tick = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.orders_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.positions_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_deals_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_orders_get = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.login = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_check = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_send = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.orders_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.positions_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_orders_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.history_deals_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_calc_margin = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.order_calc_profit = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.version = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbols_total = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.symbol_select = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.market_book_add = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.market_book_release = mocker.MagicMock()  # type: ignore[attr-defined]
        mock_mt5.market_book_get = mocker.MagicMock()  # type: ignore[attr-defined]
        yield mock_mt5


class TestMt5ReportClient:
    """Tests for Mt5ReportClient class."""

    def test_print_json(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_json method."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        test_data = {"key": "value", "number": 123}

        client.print_json(test_data)

        captured = capsys.readouterr()
        assert '"key": "value"' in captured.out
        assert '"number": 123' in captured.out

    def test_print_df(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_df method."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        test_df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

        client.print_df(test_df)

        captured = capsys.readouterr()
        assert "A" in captured.out
        assert "B" in captured.out

    def test_drop_duplicates_in_sqlite3(
        self, mock_mt5_import: ModuleType | None, mocker: MockerFixture
    ) -> None:
        """Test drop_duplicates_in_sqlite3 method."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_cursor = mocker.MagicMock()

        client.drop_duplicates_in_sqlite3(mock_cursor, "test_table", ["id", "name"])

        mock_cursor.execute.assert_called_once()

    def test_write_df_to_csv(
        self, mock_mt5_import: ModuleType | None, tmp_path: Path
    ) -> None:
        """Test write_df_to_csv method."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        test_df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        csv_path = tmp_path / "test.csv"

        client.write_df_to_csv(test_df, csv_file_path=str(csv_path))

        assert csv_path.exists()

    def test_write_df_to_sqlite3(
        self,
        mock_mt5_import: ModuleType | None,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Test write_df_to_sqlite3 method."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        test_df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        sqlite_path = tmp_path / "test.db"

        # Mock the to_sql method to avoid actual database operations
        mocker.patch.object(test_df, "to_sql")
        mock_connect = mocker.patch("sqlite3.connect")
        mock_cursor = mocker.MagicMock()
        mock_connect.return_value.__enter__.return_value.cursor.return_value = (
            mock_cursor
        )

        client.write_df_to_sqlite3(
            test_df, sqlite3_file_path=str(sqlite_path), table="test_table"
        )

        mock_connect.assert_called_once_with(str(sqlite_path))

    def test_print_history_deals(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_history_deals method."""
        assert mock_mt5_import is not None

        class MockDeal:
            def _asdict(self) -> dict[str, Any]:
                return {"ticket": 123, "symbol": "EURUSD", "profit": 10.0}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_get.return_value = [MockDeal()]

        client.initialize()
        client.print_history_deals(hours=24)

        captured = capsys.readouterr()
        assert "symbol" in captured.out

    def test_print_orders(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_orders method."""
        assert mock_mt5_import is not None

        class MockOrder:
            def _asdict(self) -> dict[str, Any]:
                return {"ticket": 456, "symbol": "GBPUSD", "volume": 0.1}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_get.return_value = [MockOrder()]

        client.initialize()
        client.print_orders()

        captured = capsys.readouterr()
        assert "symbol" in captured.out

    def test_print_positions(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_positions method."""
        assert mock_mt5_import is not None

        class MockPosition:
            def _asdict(self) -> dict[str, Any]:
                return {"ticket": 789, "symbol": "USDJPY", "profit": 5.0}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_get.return_value = [MockPosition()]

        client.initialize()
        client.print_positions()

        captured = capsys.readouterr()
        assert "symbol" in captured.out

    def test_print_margins(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_margins method."""
        assert mock_mt5_import is not None

        class MockAccountInfo:
            currency = "USD"

            def _asdict(self) -> dict[str, Any]:
                return {"currency": "USD"}

        class MockSymbolInfo:
            volume_min = 0.01

            def _asdict(self) -> dict[str, Any]:
                return {"volume_min": 0.01}

        class MockSymbolInfoTick:
            ask = 1.1234
            bid = 1.1230

            def _asdict(self) -> dict[str, Any]:
                return {"ask": 1.1234, "bid": 1.1230}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.account_info.return_value = MockAccountInfo()
        mock_mt5_import.symbol_info.return_value = MockSymbolInfo()
        mock_mt5_import.symbol_info_tick.return_value = MockSymbolInfoTick()
        mock_mt5_import.order_calc_margin.return_value = 100.0
        mock_mt5_import.ORDER_TYPE_BUY = 0
        mock_mt5_import.ORDER_TYPE_SELL = 1

        client.initialize()
        client.print_margins("EURUSD")

        captured = capsys.readouterr()
        assert "symbol" in captured.out

    def test_print_ticks(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_ticks method."""
        assert mock_mt5_import is not None

        class MockSymbolInfoTick:
            time = 1640995200

            def _asdict(self) -> dict[str, Any]:
                return {"time": 1640995200}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True

        # Mock required constants
        mock_mt5_import.COPY_TICKS_ALL = 3

        # Mock symbol info tick for non-date_to path
        mock_mt5_import.symbol_info_tick.return_value = MockSymbolInfoTick()

        # Create mock data with structured array like MetaTrader5 returns
        dt = np.dtype([
            ("time", "int64"),
            ("bid", "float64"),
            ("ask", "float64"),
            ("last", "float64"),
            ("volume", "int64"),
            ("time_msc", "int64"),
            ("flags", "int32"),
            ("volume_real", "float64"),
        ])
        mock_ticks = np.array(
            [(1640995200, 1.1230, 1.1234, 1.1232, 1, 1640995200000, 2, 1.0)], dtype=dt
        )
        mock_mt5_import.copy_ticks_from.return_value = mock_ticks

        client.initialize()
        client.print_ticks("EURUSD", seconds=60)

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_ticks_with_date_to(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_ticks method with date_to parameter."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True

        # Mock required constants
        mock_mt5_import.COPY_TICKS_ALL = 3

        # Create mock data with structured array like MetaTrader5 returns

        dt = np.dtype([
            ("time", "int64"),
            ("bid", "float64"),
            ("ask", "float64"),
            ("last", "float64"),
            ("volume", "int64"),
            ("time_msc", "int64"),
            ("flags", "int32"),
            ("volume_real", "float64"),
        ])
        mock_ticks = np.array(
            [(1640995200, 1.1230, 1.1234, 1.1232, 1, 1640995200000, 2, 1.0)], dtype=dt
        )
        mock_mt5_import.copy_ticks_range.return_value = mock_ticks

        client.initialize()
        client.print_ticks("EURUSD", seconds=60, date_to="2022-01-01 12:00:00")

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_rates(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_rates method."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True

        # Mock required constants
        mock_mt5_import.TIMEFRAME_M1 = 1

        # Create mock data with structured array like MetaTrader5 returns

        dt = np.dtype([
            ("time", "int64"),
            ("open", "float64"),
            ("high", "float64"),
            ("low", "float64"),
            ("close", "float64"),
            ("tick_volume", "int64"),
            ("spread", "int32"),
            ("real_volume", "int64"),
        ])
        mock_rates = np.array(
            [(1640995200, 1.1230, 1.1240, 1.1220, 1.1235, 100, 1, 0)], dtype=dt
        )
        mock_mt5_import.copy_rates_from_pos.return_value = mock_rates

        client.initialize()
        client.print_rates("EURUSD", granularity="M1", count=10)

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_symbol_info(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_symbol_info method."""
        assert mock_mt5_import is not None

        class MockSymbolInfo:
            def _asdict(self) -> dict[str, Any]:
                return {
                    "name": "EURUSD",
                    "bid": 1.1230,
                    "ask": 1.1234,
                    "volume_min": 0.01,
                }

        class MockSymbolInfoTick:
            def _asdict(self) -> dict[str, Any]:
                return {"time": 1640995200, "bid": 1.1230, "ask": 1.1234, "volume": 1}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbol_info.return_value = MockSymbolInfo()
        mock_mt5_import.symbol_info_tick.return_value = MockSymbolInfoTick()

        client.initialize()
        client.print_symbol_info("EURUSD")

        captured = capsys.readouterr()
        assert "name" in captured.out

    def test_print_mt5_info(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_mt5_info method."""
        assert mock_mt5_import is not None

        class MockTerminalInfo:
            def _asdict(self) -> dict[str, Any]:
                return {"company": "Test Company", "path": "/test/path"}

        class MockAccountInfo:
            def _asdict(self) -> dict[str, Any]:
                return {"login": 12345, "server": "Test-Server"}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.__version__ = "5.0.45"
        mock_mt5_import.__author__ = "MetaQuotes Ltd."
        mock_mt5_import.version.return_value = (5, 0, 4560)
        mock_mt5_import.terminal_info.return_value = MockTerminalInfo()
        mock_mt5_import.account_info.return_value = MockAccountInfo()
        mock_mt5_import.symbols_total.return_value = 1000

        client.initialize()
        client.print_mt5_info()

        captured = capsys.readouterr()
        assert "MetaTrader5" in captured.out
        assert "terminal" in captured.out
        assert "account" in captured.out
        assert "symbols_total" in captured.out

    def test_print_symbols(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_symbols method."""
        assert mock_mt5_import is not None

        class MockSymbol:
            def _asdict(self) -> dict[str, Any]:
                return {"name": "EURUSD", "bid": 1.1230, "ask": 1.1234}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbols_get.return_value = [MockSymbol()]

        client.initialize()
        client.print_symbols()

        captured = capsys.readouterr()
        assert "name" in captured.out

    def test_print_symbols_empty(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_symbols method with empty results."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.symbols_get.return_value = ()

        client.initialize()
        client.print_symbols()

        captured = capsys.readouterr()
        assert "Empty DataFrame" in captured.out

    def test_print_history_orders(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_history_orders method."""
        assert mock_mt5_import is not None

        class MockOrder:
            def _asdict(self) -> dict[str, Any]:
                return {"ticket": 456, "symbol": "GBPUSD", "volume": 0.1}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = [MockOrder()]

        client.initialize()
        client.print_history_orders(hours=24)

        captured = capsys.readouterr()
        assert "symbol" in captured.out

    def test_print_history_orders_empty(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_history_orders method with empty results."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_orders_get.return_value = ()

        client.initialize()
        client.print_history_orders(hours=24)

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_account_info(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_account_info method."""
        assert mock_mt5_import is not None

        class MockAccountInfo:
            def _asdict(self) -> dict[str, Any]:
                return {"login": 12345, "server": "Test-Server"}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.account_info.return_value = MockAccountInfo()

        client.initialize()
        client.print_account_info()

        captured = capsys.readouterr()
        assert "login" in captured.out

    def test_print_terminal_info(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_terminal_info method."""
        assert mock_mt5_import is not None

        class MockTerminalInfo:
            def _asdict(self) -> dict[str, Any]:
                return {"company": "Test Company", "path": "/test/path"}

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.terminal_info.return_value = MockTerminalInfo()

        client.initialize()
        client.print_terminal_info()

        captured = capsys.readouterr()
        assert "company" in captured.out

    def test_print_history_deals_empty(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_history_deals method with empty results."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.history_deals_get.return_value = ()

        client.initialize()
        client.print_history_deals(hours=24)

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_orders_empty(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_orders method with empty results."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.orders_get.return_value = ()

        client.initialize()
        client.print_orders()

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_positions_empty(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_positions method with empty results."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.positions_get.return_value = ()

        client.initialize()
        client.print_positions()

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_ticks_empty(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_ticks method with empty results."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.COPY_TICKS_ALL = 3
        tick_dtype = np.dtype([
            ("time", "int64"),
            ("time_msc", "int64"),
            ("bid", "float64"),
            ("ask", "float64"),
        ])
        mock_mt5_import.copy_ticks_range.return_value = np.array([], dtype=tick_dtype)

        client.initialize()
        client.print_ticks("EURUSD", seconds=60, date_to="2022-01-01 12:00:00")

        captured = capsys.readouterr()
        assert "Empty DataFrame" in captured.out

    def test_print_rates_empty(
        self, mock_mt5_import: ModuleType | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_rates method with empty results."""
        assert mock_mt5_import is not None

        client = Mt5ReportClient(mt5=mock_mt5_import)
        mock_mt5_import.initialize.return_value = True
        mock_mt5_import.TIMEFRAME_M1 = 1
        rate_dtype = np.dtype([
            ("time", "int64"),
            ("open", "float64"),
            ("high", "float64"),
            ("low", "float64"),
            ("close", "float64"),
        ])
        mock_mt5_import.copy_rates_from_pos.return_value = np.array(
            [], dtype=rate_dtype
        )

        client.initialize()
        client.print_rates("EURUSD", granularity="M1", count=10)

        captured = capsys.readouterr()
        assert "Empty DataFrame" in captured.out
