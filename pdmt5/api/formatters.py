"""Response formatters for JSON and Apache Parquet formats."""

from __future__ import annotations

import io
from typing import Any

import pandas as pd
import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]
from fastapi.responses import Response, StreamingResponse

from .models import DataResponse, ResponseFormat


def format_dataframe_to_json(
    dataframe: pd.DataFrame,
    *,
    orient: str = "records",
) -> DataResponse:
    """Format DataFrame as JSON response.

    Args:
        dataframe: DataFrame to format.
        orient: JSON orientation (records, index, columns, etc.).

    Returns:
        DataResponse model with JSON data.
    """
    # Convert DataFrame to dict/list based on orientation
    if orient == "records":
        data_value: list[dict[str, Any]] | dict[str, Any] = dataframe.to_dict(
            orient=orient  # type: ignore[arg-type]
        )
    else:
        data_value = dataframe.to_dict(orient=orient)  # type: ignore[arg-type]

    return DataResponse(
        data=data_value,
        count=len(dataframe),
        format=ResponseFormat.JSON,
    )


def format_dict_to_json(data: dict[str, Any]) -> DataResponse:
    """Format dictionary as JSON response.

    Args:
        data: Dictionary to format.

    Returns:
        DataResponse model with JSON data.
    """
    return DataResponse(
        data=data,
        count=1,
        format=ResponseFormat.JSON,
    )


def format_dataframe_to_parquet(dataframe: pd.DataFrame) -> Response:
    """Format DataFrame as Apache Parquet response.

    Args:
        dataframe: DataFrame to format.

    Returns:
        StreamingResponse with Parquet binary data.
    """
    # Convert DataFrame to Arrow Table
    table = pa.Table.from_pandas(dataframe, preserve_index=False)

    # Write to in-memory buffer
    buffer = io.BytesIO()
    pq.write_table(
        table,
        buffer,
        compression="snappy",
        use_dictionary=True,
        write_statistics=True,
    )
    buffer.seek(0)

    return StreamingResponse(
        content=iter([buffer.getvalue()]),
        media_type="application/parquet",
        headers={
            "Content-Disposition": "attachment; filename=data.parquet",
        },
    )


def format_dict_to_parquet(data: dict[str, Any]) -> Response:
    """Format dictionary as Apache Parquet response.

    Args:
        data: Dictionary to format (will be converted to single-row DataFrame).

    Returns:
        StreamingResponse with Parquet binary data.
    """
    # Convert dict to single-row DataFrame
    dataframe = pd.DataFrame([data])
    return format_dataframe_to_parquet(dataframe)
