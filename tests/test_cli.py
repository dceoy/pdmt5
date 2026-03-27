"""Tests for pdmt5.cli module."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest
from pytest_mock import MockerFixture  # noqa: TC002

from pdmt5.cli import (
    TICK_FLAG_MAP,
    TIMEFRAME_MAP,
    _build_parser,  # type: ignore[reportPrivateUsage]
    _fetch_info,  # type: ignore[reportPrivateUsage]
    _fetch_rates,  # type: ignore[reportPrivateUsage]
    _fetch_ticks,  # type: ignore[reportPrivateUsage]
    _fetch_trading,  # type: ignore[reportPrivateUsage]
    detect_format,
    export_dataframe,
    fetch_data,
    main,
    parse_datetime,
    parse_tick_flags,
    parse_timeframe,
)


class TestDetectFormat:
    """Tests for detect_format."""

    def test_explicit_format_returned(self, tmp_path: Path) -> None:
        """Test that explicit format overrides extension."""
        result = detect_format(tmp_path / "data.txt", explicit_format="csv")
        assert result == "csv"

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("data.csv", "csv"),
            ("data.json", "json"),
            ("data.parquet", "parquet"),
            ("data.pq", "parquet"),
            ("data.db", "sqlite3"),
            ("data.sqlite", "sqlite3"),
            ("data.sqlite3", "sqlite3"),
            ("DATA.CSV", "csv"),
            ("DATA.JSON", "json"),
            ("DATA.PARQUET", "parquet"),
        ],
    )
    def test_auto_detect_from_extension(
        self,
        tmp_path: Path,
        filename: str,
        expected: str,
    ) -> None:
        """Test format auto-detection from file extension."""
        result = detect_format(tmp_path / filename)
        assert result == expected

    def test_unknown_extension_raises(self, tmp_path: Path) -> None:
        """Test that unknown extension raises ValueError."""
        with pytest.raises(ValueError, match="Cannot detect format"):
            detect_format(tmp_path / "data.xyz")


class TestExportDataframe:
    """Tests for export_dataframe."""

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})

    def test_export_csv(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """Test CSV export."""
        output = tmp_path / "out.csv"
        export_dataframe(sample_df, output, "csv")
        result = pd.read_csv(output)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_export_json(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """Test JSON export."""
        output = tmp_path / "out.json"
        export_dataframe(sample_df, output, "json")
        with output.open() as f:
            records = json.load(f)
        assert len(records) == 3
        assert records[0]["a"] == 1

    def test_export_parquet(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """Test Parquet export."""
        output = tmp_path / "out.parquet"
        export_dataframe(sample_df, output, "parquet")
        result = pd.read_parquet(output)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_export_sqlite3(self, tmp_path: Path, sample_df: pd.DataFrame) -> None:
        """Test SQLite3 export."""
        output = tmp_path / "out.db"
        export_dataframe(sample_df, output, "sqlite3", table_name="test_table")
        with sqlite3.connect(output) as conn:
            result = pd.read_sql(  # type: ignore[reportUnknownMemberType]
                "SELECT * FROM test_table",
                conn,
            )
        pd.testing.assert_frame_equal(result, sample_df)

    def test_unsupported_format_raises(
        self,
        tmp_path: Path,
        sample_df: pd.DataFrame,
    ) -> None:
        """Test that unsupported format raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported output format"):
            export_dataframe(sample_df, tmp_path / "out.txt", "xml")


class TestParseDatetime:
    """Tests for parse_datetime."""

    def test_valid_date(self) -> None:
        """Test parsing a date string."""
        result = parse_datetime("2024-01-15")
        assert result == datetime(2024, 1, 15, tzinfo=UTC)

    def test_valid_datetime_with_tz(self) -> None:
        """Test parsing a datetime with timezone."""
        result = parse_datetime("2024-01-15T12:00:00+00:00")
        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    def test_invalid_format_raises(self) -> None:
        """Test that invalid format raises ArgumentTypeError."""
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid datetime"):
            parse_datetime("not-a-date")


class TestParseTimeframe:
    """Tests for parse_timeframe."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("M1", 1), ("h1", 16385), ("D1", 16408), ("MN1", 49153)],
    )
    def test_named_timeframe(self, value: str, expected: int) -> None:
        """Test parsing named timeframes."""
        assert parse_timeframe(value) == expected

    def test_integer_timeframe(self) -> None:
        """Test parsing integer timeframe."""
        assert parse_timeframe("42") == 42

    def test_invalid_timeframe_raises(self) -> None:
        """Test that invalid timeframe raises ArgumentTypeError."""
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid timeframe"):
            parse_timeframe("INVALID")


class TestParseTickFlags:
    """Tests for parse_tick_flags."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("ALL", 1), ("info", 2), ("TRADE", 4)],
    )
    def test_named_flag(self, value: str, expected: int) -> None:
        """Test parsing named tick flags."""
        assert parse_tick_flags(value) == expected

    def test_integer_flag(self) -> None:
        """Test parsing integer tick flag."""
        assert parse_tick_flags("7") == 7

    def test_invalid_flag_raises(self) -> None:
        """Test that invalid flag raises ArgumentTypeError."""
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid tick flags"):
            parse_tick_flags("INVALID")


class TestConstants:
    """Tests for module constants."""

    def test_timeframe_map_has_expected_keys(self) -> None:
        """Test that TIMEFRAME_MAP contains standard timeframes."""
        for key in ("M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"):
            assert key in TIMEFRAME_MAP

    def test_tick_flag_map_has_expected_keys(self) -> None:
        """Test that TICK_FLAG_MAP contains standard flags."""
        assert set(TICK_FLAG_MAP) == {"ALL", "INFO", "TRADE"}


def _make_args(**kwargs: object) -> argparse.Namespace:
    """Create an argparse.Namespace with given attributes."""
    return argparse.Namespace(**kwargs)


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock Mt5DataClient."""
    client = MagicMock()
    sample_df = pd.DataFrame({"col": [1]})
    client.copy_rates_from_as_df.return_value = sample_df
    client.copy_rates_from_pos_as_df.return_value = sample_df
    client.copy_rates_range_as_df.return_value = sample_df
    client.copy_ticks_from_as_df.return_value = sample_df
    client.copy_ticks_range_as_df.return_value = sample_df
    client.account_info_as_df.return_value = sample_df
    client.terminal_info_as_df.return_value = sample_df
    client.symbols_get_as_df.return_value = sample_df
    client.symbol_info_as_df.return_value = sample_df
    client.orders_get_as_df.return_value = sample_df
    client.positions_get_as_df.return_value = sample_df
    client.history_orders_get_as_df.return_value = sample_df
    client.history_deals_get_as_df.return_value = sample_df
    return client


class TestFetchRates:
    """Tests for _fetch_rates."""

    def test_rates_from(self, mock_client: MagicMock) -> None:
        """Test rates-from command dispatches correctly."""
        dt = datetime(2024, 1, 1, tzinfo=UTC)
        args = _make_args(
            command="rates-from",
            symbol="EURUSD",
            timeframe=1,
            date_from=dt,
            count=100,
        )
        _fetch_rates(mock_client, args)
        mock_client.copy_rates_from_as_df.assert_called_once_with(
            symbol="EURUSD",
            timeframe=1,
            date_from=dt,
            count=100,
        )

    def test_rates_from_pos(self, mock_client: MagicMock) -> None:
        """Test rates-from-pos command dispatches correctly."""
        args = _make_args(
            command="rates-from-pos",
            symbol="GBPUSD",
            timeframe=16385,
            start_pos=0,
            count=50,
        )
        _fetch_rates(mock_client, args)
        mock_client.copy_rates_from_pos_as_df.assert_called_once_with(
            symbol="GBPUSD",
            timeframe=16385,
            start_pos=0,
            count=50,
        )

    def test_rates_range(self, mock_client: MagicMock) -> None:
        """Test rates-range command dispatches correctly."""
        dt_from = datetime(2024, 1, 1, tzinfo=UTC)
        dt_to = datetime(2024, 2, 1, tzinfo=UTC)
        args = _make_args(
            command="rates-range",
            symbol="USDJPY",
            timeframe=16408,
            date_from=dt_from,
            date_to=dt_to,
        )
        _fetch_rates(mock_client, args)
        mock_client.copy_rates_range_as_df.assert_called_once_with(
            symbol="USDJPY",
            timeframe=16408,
            date_from=dt_from,
            date_to=dt_to,
        )


class TestFetchTicks:
    """Tests for _fetch_ticks."""

    def test_ticks_from(self, mock_client: MagicMock) -> None:
        """Test ticks-from command dispatches correctly."""
        dt = datetime(2024, 1, 1, tzinfo=UTC)
        args = _make_args(
            command="ticks-from",
            symbol="EURUSD",
            date_from=dt,
            count=100,
            flags=1,
        )
        _fetch_ticks(mock_client, args)
        mock_client.copy_ticks_from_as_df.assert_called_once_with(
            symbol="EURUSD",
            date_from=dt,
            count=100,
            flags=1,
        )

    def test_ticks_range(self, mock_client: MagicMock) -> None:
        """Test ticks-range command dispatches correctly."""
        dt_from = datetime(2024, 1, 1, tzinfo=UTC)
        dt_to = datetime(2024, 2, 1, tzinfo=UTC)
        args = _make_args(
            command="ticks-range",
            symbol="EURUSD",
            date_from=dt_from,
            date_to=dt_to,
            flags=2,
        )
        _fetch_ticks(mock_client, args)
        mock_client.copy_ticks_range_as_df.assert_called_once_with(
            symbol="EURUSD",
            date_from=dt_from,
            date_to=dt_to,
            flags=2,
        )


class TestFetchInfo:
    """Tests for _fetch_info."""

    def test_account_info(self, mock_client: MagicMock) -> None:
        """Test account-info command dispatches correctly."""
        args = _make_args(command="account-info")
        _fetch_info(mock_client, args)
        mock_client.account_info_as_df.assert_called_once()

    def test_terminal_info(self, mock_client: MagicMock) -> None:
        """Test terminal-info command dispatches correctly."""
        args = _make_args(command="terminal-info")
        _fetch_info(mock_client, args)
        mock_client.terminal_info_as_df.assert_called_once()

    def test_symbols(self, mock_client: MagicMock) -> None:
        """Test symbols command dispatches correctly."""
        args = _make_args(command="symbols", group="*USD*")
        _fetch_info(mock_client, args)
        mock_client.symbols_get_as_df.assert_called_once_with(group="*USD*")

    def test_symbol_info(self, mock_client: MagicMock) -> None:
        """Test symbol-info command dispatches correctly."""
        args = _make_args(command="symbol-info", symbol="EURUSD")
        _fetch_info(mock_client, args)
        mock_client.symbol_info_as_df.assert_called_once_with(symbol="EURUSD")


class TestFetchTrading:
    """Tests for _fetch_trading."""

    def test_orders(self, mock_client: MagicMock) -> None:
        """Test orders command dispatches correctly."""
        args = _make_args(
            command="orders",
            symbol="EURUSD",
            group=None,
            ticket=None,
        )
        _fetch_trading(mock_client, args)
        mock_client.orders_get_as_df.assert_called_once_with(
            symbol="EURUSD",
            group=None,
            ticket=None,
        )

    def test_positions(self, mock_client: MagicMock) -> None:
        """Test positions command dispatches correctly."""
        args = _make_args(
            command="positions",
            symbol=None,
            group="*USD*",
            ticket=None,
        )
        _fetch_trading(mock_client, args)
        mock_client.positions_get_as_df.assert_called_once_with(
            symbol=None,
            group="*USD*",
            ticket=None,
        )

    def test_history_orders(self, mock_client: MagicMock) -> None:
        """Test history-orders command dispatches correctly."""
        dt_from = datetime(2024, 1, 1, tzinfo=UTC)
        dt_to = datetime(2024, 2, 1, tzinfo=UTC)
        args = _make_args(
            command="history-orders",
            date_from=dt_from,
            date_to=dt_to,
            group=None,
            symbol="EURUSD",
            ticket=None,
            position=None,
        )
        _fetch_trading(mock_client, args)
        mock_client.history_orders_get_as_df.assert_called_once_with(
            date_from=dt_from,
            date_to=dt_to,
            group=None,
            symbol="EURUSD",
            ticket=None,
            position=None,
        )

    def test_history_deals(self, mock_client: MagicMock) -> None:
        """Test history-deals command dispatches correctly."""
        dt_from = datetime(2024, 1, 1, tzinfo=UTC)
        dt_to = datetime(2024, 2, 1, tzinfo=UTC)
        args = _make_args(
            command="history-deals",
            date_from=dt_from,
            date_to=dt_to,
            group=None,
            symbol=None,
            ticket=12345,
            position=None,
        )
        _fetch_trading(mock_client, args)
        mock_client.history_deals_get_as_df.assert_called_once_with(
            date_from=dt_from,
            date_to=dt_to,
            group=None,
            symbol=None,
            ticket=12345,
            position=None,
        )


class TestFetchData:
    """Tests for fetch_data dispatch."""

    @pytest.mark.parametrize(
        "command",
        ["rates-from", "rates-from-pos", "rates-range"],
    )
    def test_rates_dispatch(
        self,
        mock_client: MagicMock,
        command: str,
    ) -> None:
        """Test that rates commands dispatch through fetch_data."""
        args = _make_args(
            command=command,
            symbol="EURUSD",
            timeframe=1,
            date_from=datetime(2024, 1, 1, tzinfo=UTC),
            date_to=datetime(2024, 2, 1, tzinfo=UTC),
            count=100,
            start_pos=0,
        )
        result = fetch_data(mock_client, args)
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize("command", ["ticks-from", "ticks-range"])
    def test_ticks_dispatch(
        self,
        mock_client: MagicMock,
        command: str,
    ) -> None:
        """Test that ticks commands dispatch through fetch_data."""
        args = _make_args(
            command=command,
            symbol="EURUSD",
            date_from=datetime(2024, 1, 1, tzinfo=UTC),
            date_to=datetime(2024, 2, 1, tzinfo=UTC),
            count=100,
            flags=1,
        )
        result = fetch_data(mock_client, args)
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize(
        "command",
        ["account-info", "terminal-info", "symbols", "symbol-info"],
    )
    def test_info_dispatch(
        self,
        mock_client: MagicMock,
        command: str,
    ) -> None:
        """Test that info commands dispatch through fetch_data."""
        args = _make_args(
            command=command,
            symbol="EURUSD",
            group=None,
        )
        result = fetch_data(mock_client, args)
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize(
        "command",
        ["orders", "positions", "history-orders", "history-deals"],
    )
    def test_trading_dispatch(
        self,
        mock_client: MagicMock,
        command: str,
    ) -> None:
        """Test that trading commands dispatch through fetch_data."""
        args = _make_args(
            command=command,
            symbol=None,
            group=None,
            ticket=None,
            position=None,
            date_from=datetime(2024, 1, 1, tzinfo=UTC),
            date_to=datetime(2024, 2, 1, tzinfo=UTC),
        )
        result = fetch_data(mock_client, args)
        assert isinstance(result, pd.DataFrame)

    def test_unknown_command_raises(self, mock_client: MagicMock) -> None:
        """Test that unknown command raises ValueError."""
        args = _make_args(command="unknown")
        with pytest.raises(ValueError, match="Unknown command"):
            fetch_data(mock_client, args)


class TestBuildParser:
    """Tests for _build_parser."""

    def test_parser_creation(self) -> None:
        """Test that parser is created successfully."""
        parser = _build_parser()
        assert parser.prog == "pdmt5"

    @pytest.mark.parametrize(
        ("argv", "expected_command"),
        [
            (
                [
                    "-o",
                    "out.csv",
                    "rates-from",
                    "--symbol",
                    "EURUSD",
                    "--timeframe",
                    "M1",
                    "--date-from",
                    "2024-01-01",
                    "--count",
                    "100",
                ],
                "rates-from",
            ),
            (
                [
                    "-o",
                    "out.csv",
                    "rates-from-pos",
                    "--symbol",
                    "EURUSD",
                    "--timeframe",
                    "H1",
                    "--start-pos",
                    "0",
                    "--count",
                    "50",
                ],
                "rates-from-pos",
            ),
            (
                [
                    "-o",
                    "out.json",
                    "rates-range",
                    "--symbol",
                    "EURUSD",
                    "--timeframe",
                    "D1",
                    "--date-from",
                    "2024-01-01",
                    "--date-to",
                    "2024-02-01",
                ],
                "rates-range",
            ),
            (
                [
                    "-o",
                    "out.csv",
                    "ticks-from",
                    "--symbol",
                    "EURUSD",
                    "--date-from",
                    "2024-01-01",
                    "--count",
                    "100",
                    "--flags",
                    "ALL",
                ],
                "ticks-from",
            ),
            (
                [
                    "-o",
                    "out.csv",
                    "ticks-range",
                    "--symbol",
                    "EURUSD",
                    "--date-from",
                    "2024-01-01",
                    "--date-to",
                    "2024-02-01",
                    "--flags",
                    "INFO",
                ],
                "ticks-range",
            ),
            (["-o", "out.csv", "account-info"], "account-info"),
            (["-o", "out.csv", "terminal-info"], "terminal-info"),
            (["-o", "out.csv", "symbols"], "symbols"),
            (
                ["-o", "out.csv", "symbol-info", "--symbol", "EURUSD"],
                "symbol-info",
            ),
            (["-o", "out.csv", "orders"], "orders"),
            (["-o", "out.csv", "positions"], "positions"),
            (
                [
                    "-o",
                    "out.csv",
                    "history-orders",
                    "--date-from",
                    "2024-01-01",
                    "--date-to",
                    "2024-02-01",
                ],
                "history-orders",
            ),
            (
                [
                    "-o",
                    "out.csv",
                    "history-deals",
                    "--ticket",
                    "12345",
                ],
                "history-deals",
            ),
        ],
    )
    def test_parse_subcommands(
        self,
        argv: list[str],
        expected_command: str,
    ) -> None:
        """Test parsing various subcommands."""
        parser = _build_parser()
        args = parser.parse_args(argv)
        assert args.command == expected_command

    def test_parse_connection_args(self) -> None:
        """Test parsing connection arguments."""
        parser = _build_parser()
        args = parser.parse_args([
            "--login",
            "12345",
            "--password",
            "secret",
            "--server",
            "Demo",
            "--path",
            "/mt5/terminal.exe",
            "--timeout",
            "5000",
            "-o",
            "out.csv",
            "account-info",
        ])
        assert args.login == 12345
        assert args.password == "secret"  # noqa: S105
        assert args.server == "Demo"
        assert args.path == "/mt5/terminal.exe"
        assert args.timeout == 5000

    def test_parse_output_args(self) -> None:
        """Test parsing output arguments."""
        parser = _build_parser()
        args = parser.parse_args([
            "-o",
            "out.db",
            "--format",
            "sqlite3",
            "--table",
            "rates",
            "account-info",
        ])
        assert args.output == Path("out.db")
        assert args.format == "sqlite3"
        assert args.table == "rates"

    def test_parse_log_level(self) -> None:
        """Test parsing log level argument."""
        parser = _build_parser()
        args = parser.parse_args([
            "--log-level",
            "DEBUG",
            "-o",
            "out.csv",
            "account-info",
        ])
        assert args.log_level == "DEBUG"


class TestMain:
    """Tests for main entry point."""

    def test_main_success(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Test successful main execution."""
        sample_df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        mock_client = MagicMock()
        mock_client.account_info_as_df.return_value = sample_df
        mocker.patch("pdmt5.cli.Mt5DataClient", return_value=mock_client)
        output = tmp_path / "out.csv"
        main(["-o", str(output), "account-info"])
        mock_client.initialize_and_login_mt5.assert_called_once()
        mock_client.shutdown.assert_called_once()
        assert output.exists()
        result = pd.read_csv(output)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_main_with_connection_args(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Test main with connection arguments."""
        mock_client = MagicMock()
        mock_client.account_info_as_df.return_value = pd.DataFrame({"a": [1]})
        mock_constructor = mocker.patch(
            "pdmt5.cli.Mt5DataClient",
            return_value=mock_client,
        )
        mocker.patch("pdmt5.cli.Mt5Config")
        output = tmp_path / "out.json"
        main([
            "--login",
            "123",
            "--password",
            "pw",
            "--server",
            "srv",
            "-o",
            str(output),
            "account-info",
        ])
        mock_constructor.assert_called_once()

    def test_main_shutdown_on_error(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Test that shutdown is called even when fetch_data raises."""
        mock_client = MagicMock()
        mock_client.account_info_as_df.side_effect = RuntimeError("MT5 error")
        mocker.patch("pdmt5.cli.Mt5DataClient", return_value=mock_client)
        output = tmp_path / "out.csv"
        with pytest.raises(RuntimeError, match="MT5 error"):
            main(["-o", str(output), "account-info"])
        mock_client.shutdown.assert_called_once()

    def test_main_format_detection_error(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Test main exits on format detection error."""
        mocker.patch("pdmt5.cli.Mt5DataClient")
        output = tmp_path / "out.xyz"
        with pytest.raises(SystemExit):
            main(["-o", str(output), "account-info"])

    def test_main_explicit_format(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Test main with explicit format flag."""
        mock_client = MagicMock()
        mock_client.account_info_as_df.return_value = pd.DataFrame({"a": [1]})
        mocker.patch("pdmt5.cli.Mt5DataClient", return_value=mock_client)
        output = tmp_path / "out.txt"
        main(["-o", str(output), "--format", "json", "account-info"])
        assert output.exists()

    def test_main_sqlite3_with_table(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Test main with SQLite3 format and custom table name."""
        mock_client = MagicMock()
        mock_client.symbols_get_as_df.return_value = pd.DataFrame({"s": ["EURUSD"]})
        mocker.patch("pdmt5.cli.Mt5DataClient", return_value=mock_client)
        output = tmp_path / "out.db"
        main([
            "-o",
            str(output),
            "--table",
            "symbols",
            "symbols",
            "--group",
            "*USD*",
        ])
        with sqlite3.connect(output) as conn:
            result = pd.read_sql(  # type: ignore[reportUnknownMemberType]
                "SELECT * FROM symbols",
                conn,
            )
        assert len(result) == 1
