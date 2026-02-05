"""Utility functions for the pdmt5 package."""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar, cast

import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Callable

P = ParamSpec("P")
R = TypeVar("R")


def detect_and_convert_time_to_datetime(
    skip_toggle: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to convert time values/columns to datetime based on result type.

    Automatically detects result type and applies appropriate time conversion:
    - dict: converts time values in the dictionary
    - list: converts time values in each dictionary item
    - DataFrame: converts time columns

    Args:
        skip_toggle: Name of the parameter to skip conversion if set to False.

    Returns:
        Decorator function.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            if skip_toggle and kwargs.get(skip_toggle):
                return result
            elif isinstance(result, dict):
                return cast(
                    "R",
                    _convert_time_values_in_dict(
                        dictionary=cast("dict[str, Any]", result)
                    ),
                )
            elif isinstance(result, list):
                return [
                    (
                        _convert_time_values_in_dict(
                            dictionary=cast("dict[str, Any]", d)
                        )
                        if isinstance(d, dict)
                        else d
                    )
                    for d in cast("list[Any]", result)
                ]  # type: ignore[return-value]
            elif isinstance(result, pd.DataFrame):
                return cast("R", _convert_time_columns_in_df(result))
            else:
                return result

        return wrapper

    return decorator


def _convert_time_values_in_dict(dictionary: dict[str, Any]) -> dict[str, Any]:
    """Convert time values in a dictionary to datetime.

    Args:
        dictionary: Dictionary to convert.

    Returns:
        Dictionary with converted time values.
    """
    new_dict = dictionary.copy()
    for k, v in new_dict.items():
        if not isinstance(v, (int, float)):
            continue
        elif k.startswith("time_") and k.endswith("_msc"):
            new_dict[k] = pd.to_datetime(v, unit="ms")
        elif k == "time" or k.startswith("time_"):
            new_dict[k] = pd.to_datetime(v, unit="s")
    return new_dict


def _convert_time_columns_in_df(df: pd.DataFrame) -> pd.DataFrame:
    """Convert time columns in DataFrame to datetime.

    Args:
        df: DataFrame to convert.

    Returns:
        DataFrame with converted time columns.
    """
    new_df = df.copy()
    for c in new_df.columns:
        if c.startswith("time_") and c.endswith("_msc"):
            new_df[c] = pd.to_datetime(new_df[c], unit="ms").astype("datetime64[ns]")
        elif c == "time" or c.startswith("time_"):
            new_df[c] = pd.to_datetime(new_df[c], unit="s").astype("datetime64[ns]")
    return new_df


def set_index_if_possible(
    index_parameters: str | None = None,
) -> Callable[[Callable[P, pd.DataFrame]], Callable[P, pd.DataFrame]]:
    """Decorator to set index on DataFrame results if not empty.

    Args:
        index_parameters: Name of the parameter to use as index if provided.

    Returns:
        Decorator function.
    """

    def decorator(
        func: Callable[P, pd.DataFrame],
    ) -> Callable[P, pd.DataFrame]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> pd.DataFrame:
            result = func(*args, **kwargs)
            if not isinstance(result, pd.DataFrame):  # type: ignore[reportUnnecessaryIsInstance]
                error_message = (
                    f"Function {func.__name__} returned non-DataFrame result: "
                    f"{type(result).__name__}. Expected DataFrame."
                )
                raise TypeError(error_message)
            elif index_parameters and kwargs.get(index_parameters) and not result.empty:
                return result.set_index(kwargs[index_parameters])
            else:
                return result

        return wrapper

    return decorator
