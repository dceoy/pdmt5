"""Test cases for pdmt5.utils module."""

# pyright: reportPrivateUsage=false

from typing import Any

import pandas as pd
import pytest

from pdmt5.utils import (
    _convert_time_columns_in_df,
    _convert_time_values_in_dict,
    detect_and_convert_time_to_datetime,
    set_index_if_possible,
)


class TestConvertTimeValuesInDict:
    """Test _convert_time_values_in_dict function."""

    def test_convert_time_values_basic(self) -> None:
        """Test basic time value conversion."""
        input_dict = {
            "time": 1704067200,  # 2024-01-01 00:00:00 UTC
            "price": 100.5,
            "volume": 1000,
        }
        result = _convert_time_values_in_dict(input_dict)

        assert isinstance(result["time"], pd.Timestamp)
        assert result["time"] == pd.Timestamp("2024-01-01 00:00:00")
        assert result["price"] == 100.5
        assert result["volume"] == 1000

    def test_convert_time_values_with_msc(self) -> None:
        """Test conversion of millisecond time values."""
        input_dict = {
            "time_msc": 1704067200000,  # 2024-01-01 00:00:00 UTC in milliseconds
            "time_setup_msc": 1704067200500,
            "other_data": "test",
        }
        result = _convert_time_values_in_dict(input_dict)

        assert isinstance(result["time_msc"], pd.Timestamp)
        assert result["time_msc"] == pd.Timestamp("2024-01-01 00:00:00")
        assert result["time_setup_msc"] == pd.Timestamp("2024-01-01 00:00:00.500")
        assert result["other_data"] == "test"

    def test_convert_time_values_with_time_prefix(self) -> None:
        """Test conversion of time-prefixed fields."""
        input_dict = {
            "time_setup": 1704067200,
            "time_done": 1704067260,
            "time_expiration": 1704067320,
            "status": "complete",
        }
        result = _convert_time_values_in_dict(input_dict)

        assert isinstance(result["time_setup"], pd.Timestamp)
        assert isinstance(result["time_done"], pd.Timestamp)
        assert isinstance(result["time_expiration"], pd.Timestamp)
        assert result["status"] == "complete"

    def test_convert_time_values_non_numeric(self) -> None:
        """Test that non-numeric values are not converted."""
        input_dict = {
            "time": "not a timestamp",
            "time_text": "2024-01-01",
            "time_none": None,
        }
        result = _convert_time_values_in_dict(input_dict)

        assert result["time"] == "not a timestamp"
        assert result["time_text"] == "2024-01-01"
        assert result["time_none"] is None

    def test_convert_time_values_empty_dict(self) -> None:
        """Test conversion of empty dictionary."""
        result = _convert_time_values_in_dict({})
        assert result == {}

    def test_convert_time_values_no_time_fields(self) -> None:
        """Test dictionary with no time fields."""
        input_dict = {"price": 100.5, "volume": 1000, "symbol": "EURUSD"}
        result = _convert_time_values_in_dict(input_dict)
        assert result == input_dict

    def test_convert_time_values_in_dict_with_time_msc_additional(self) -> None:
        """Test _convert_time_values_in_dict with time_msc fields."""
        test_dict = {
            "time_setup_msc": 1640995200000,
            "time_done_msc": 1640995210000,
            "regular_field": "unchanged",
            "numeric_field": 123.45,
        }

        result = _convert_time_values_in_dict(test_dict)

        assert isinstance(result["time_setup_msc"], pd.Timestamp)
        assert isinstance(result["time_done_msc"], pd.Timestamp)
        assert result["regular_field"] == "unchanged"
        assert result["numeric_field"] == 123.45

    def test_convert_time_values_in_dict_with_time_fields_additional(self) -> None:
        """Test _convert_time_values_in_dict with regular time fields."""
        test_dict = {
            "time": 1640995200,
            "time_setup": 1640995210,
            "time_update": 1640995220,
            "regular_field": "unchanged",
            "string_field": "not_time",
        }

        result = _convert_time_values_in_dict(test_dict)

        assert isinstance(result["time"], pd.Timestamp)
        assert isinstance(result["time_setup"], pd.Timestamp)
        assert isinstance(result["time_update"], pd.Timestamp)
        assert result["regular_field"] == "unchanged"
        assert result["string_field"] == "not_time"


class TestConvertTimeColumnsInDf:
    """Test _convert_time_columns_in_df function."""

    def test_convert_time_columns_basic(self) -> None:
        """Test basic time column conversion."""
        data_df = pd.DataFrame({
            "time": [1704067200, 1704067260, 1704067320],
            "price": [100.5, 100.6, 100.7],
        })
        result = _convert_time_columns_in_df(data_df)

        assert result["time"].dtype == "datetime64[ns]"
        assert result["time"].iloc[0] == pd.Timestamp("2024-01-01 00:00:00")
        assert result["price"].dtype == float

    def test_convert_time_columns_with_msc(self) -> None:
        """Test conversion of millisecond time columns."""
        data_df = pd.DataFrame({
            "time_msc": [1704067200000, 1704067200500],
            "time_setup_msc": [1704067201000, 1704067201500],
            "volume": [100, 200],
        })
        result = _convert_time_columns_in_df(data_df)

        assert result["time_msc"].dtype == "datetime64[ns]"
        assert result["time_setup_msc"].dtype == "datetime64[ns]"
        assert result["time_msc"].iloc[0] == pd.Timestamp("2024-01-01 00:00:00")
        assert result["time_setup_msc"].iloc[1] == pd.Timestamp(
            "2024-01-01 00:00:01.500"
        )

    def test_convert_time_columns_with_time_prefix(self) -> None:
        """Test conversion of time-prefixed columns."""
        data_df = pd.DataFrame({
            "time_setup": [1704067200, 1704067260],
            "time_done": [1704067260, 1704067320],
            "status": ["pending", "complete"],
        })
        result = _convert_time_columns_in_df(data_df)

        assert result["time_setup"].dtype == "datetime64[ns]"
        assert result["time_done"].dtype == "datetime64[ns]"
        assert result["status"].dtype == object

    def test_convert_time_columns_empty_df(self) -> None:
        """Test conversion of empty DataFrame."""
        empty_df = pd.DataFrame()
        result = _convert_time_columns_in_df(empty_df)
        assert result.empty

    def test_convert_time_columns_no_time_columns(self) -> None:
        """Test DataFrame with no time columns."""
        data_df = pd.DataFrame({
            "price": [100.5, 100.6],
            "volume": [1000, 2000],
            "symbol": ["EURUSD", "GBPUSD"],
        })
        result = _convert_time_columns_in_df(data_df)
        pd.testing.assert_frame_equal(result, data_df)


class TestDetectAndConvertTimeToDatetime:
    """Test detect_and_convert_time_to_datetime decorator."""

    def test_decorator_with_dict_result(self) -> None:
        """Test decorator with function returning dict."""

        @detect_and_convert_time_to_datetime()
        def get_data() -> dict[str, Any]:
            return {"time": 1704067200, "price": 100.5}

        result = get_data()
        assert isinstance(result["time"], pd.Timestamp)
        assert result["time"] == pd.Timestamp("2024-01-01 00:00:00")

    def test_decorator_with_list_result(self) -> None:
        """Test decorator with function returning list of dicts."""

        @detect_and_convert_time_to_datetime()
        def get_data() -> list[dict[str, Any]]:
            return [
                {"time": 1704067200, "price": 100.5},
                {"time": 1704067260, "price": 100.6},
            ]

        result = get_data()
        assert len(result) == 2
        assert all(isinstance(d["time"], pd.Timestamp) for d in result)

    def test_decorator_with_dataframe_result(self) -> None:
        """Test decorator with function returning DataFrame."""

        @detect_and_convert_time_to_datetime()
        def get_data() -> pd.DataFrame:
            return pd.DataFrame({
                "time": [1704067200, 1704067260],
                "price": [100.5, 100.6],
            })

        result = get_data()
        assert result["time"].dtype == "datetime64[ns]"

    def test_decorator_with_skip_toggle(self) -> None:
        """Test decorator with skip_toggle parameter."""

        @detect_and_convert_time_to_datetime(skip_toggle="skip_to_datetime")
        def get_data(skip_to_datetime: bool = False) -> dict[str, Any]:  # noqa: ARG001
            return {"time": 1704067200, "price": 100.5}

        # With conversion (default)
        result1 = get_data(skip_to_datetime=False)
        assert isinstance(result1["time"], pd.Timestamp)

        # Without conversion
        result2 = get_data(skip_to_datetime=True)
        assert isinstance(result2["time"], int)
        assert result2["time"] == 1704067200

    def test_decorator_with_other_result_type(self) -> None:
        """Test decorator with function returning other types."""

        @detect_and_convert_time_to_datetime()
        def get_string() -> str:
            return "test string"

        @detect_and_convert_time_to_datetime()
        def get_number() -> int:
            return 42

        @detect_and_convert_time_to_datetime()
        def get_none() -> None:
            return None

        assert get_string() == "test string"
        assert get_number() == 42
        assert get_none() is None

    def test_decorator_with_list_of_mixed_types(self) -> None:
        """Test decorator with list containing mixed types."""

        @detect_and_convert_time_to_datetime()
        def get_data() -> list[Any]:
            return [
                {"time": 1704067200, "price": 100.5},
                "not a dict",
                42,
                None,
            ]

        result = get_data()
        assert isinstance(result[0]["time"], pd.Timestamp)
        assert result[1] == "not a dict"
        assert result[2] == 42
        assert result[3] is None


class TestSetIndexIfPossible:
    """Test set_index_if_possible decorator."""

    def test_decorator_with_index_parameter(self) -> None:
        """Test decorator with index parameter provided."""

        @set_index_if_possible(index_parameters="index_keys")
        def get_data(index_keys: str | None = None) -> pd.DataFrame:  # noqa: ARG001
            return pd.DataFrame({
                "symbol": ["EURUSD", "GBPUSD"],
                "price": [1.1, 1.3],
            })

        result = get_data(index_keys="symbol")
        assert result.index.name == "symbol"
        assert list(result.index) == ["EURUSD", "GBPUSD"]

    def test_decorator_without_index_parameter(self) -> None:
        """Test decorator without index parameter."""

        @set_index_if_possible(index_parameters="index_keys")
        def get_data(index_keys: str | None = None) -> pd.DataFrame:  # noqa: ARG001
            return pd.DataFrame({
                "symbol": ["EURUSD", "GBPUSD"],
                "price": [1.1, 1.3],
            })

        result = get_data()
        assert isinstance(result.index, pd.RangeIndex)

    def test_decorator_with_empty_dataframe(self) -> None:
        """Test decorator with empty DataFrame."""

        @set_index_if_possible(index_parameters="index_keys")
        def get_data(index_keys: str | None = None) -> pd.DataFrame:  # noqa: ARG001
            return pd.DataFrame()

        result = get_data(index_keys="symbol")
        assert result.empty

    def test_decorator_with_non_dataframe_raises(self) -> None:
        """Test decorator raises TypeError for non-DataFrame return."""

        @set_index_if_possible(index_parameters="index_keys")
        def get_data(index_keys: str | None = None) -> dict[str, Any]:  # noqa: ARG001
            return {"data": "not a dataframe"}

        with pytest.raises(
            TypeError,
            match=(
                r"Function get_data returned non-DataFrame result: "
                r"dict\. Expected DataFrame\."
            ),
        ):
            get_data()

    def test_decorator_with_no_index_parameters(self) -> None:
        """Test decorator with no index_parameters specified."""

        @set_index_if_possible()
        def get_data() -> pd.DataFrame:
            return pd.DataFrame({
                "symbol": ["EURUSD", "GBPUSD"],
                "price": [1.1, 1.3],
            })

        result = get_data()
        assert isinstance(result.index, pd.RangeIndex)

    def test_decorator_preserves_function_metadata(self) -> None:
        """Test decorator preserves original function metadata."""

        @set_index_if_possible(index_parameters="index_keys")
        def get_data(index_keys: str | None = None) -> pd.DataFrame:  # noqa: ARG001
            """Get test data."""
            return pd.DataFrame()

        assert get_data.__name__ == "get_data"
        assert get_data.__doc__ == "Get test data."

    def test_decorator_with_multiple_columns_index(self) -> None:
        """Test decorator with list of columns as index."""

        @set_index_if_possible(index_parameters="index_keys")
        def get_data(index_keys: list[str] | None = None) -> pd.DataFrame:  # noqa: ARG001
            return pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02"],
                "symbol": ["EURUSD", "GBPUSD"],
                "price": [1.1, 1.3],
            })

        result = get_data(index_keys=["date", "symbol"])
        assert isinstance(result.index, pd.MultiIndex)
        assert result.index.names == ["date", "symbol"]
