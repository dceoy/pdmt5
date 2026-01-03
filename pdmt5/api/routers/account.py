"""Account and terminal information endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from pdmt5.api.auth import verify_api_key
from pdmt5.api.dependencies import (
    get_mt5_client,
    get_response_format,
    run_in_threadpool,
)
from pdmt5.api.formatters import (
    format_dataframe_to_json,
    format_dataframe_to_parquet,
)
from pdmt5.api.models import (
    AccountInfoRequest,
    DataResponse,
    ResponseFormat,
    TerminalInfoRequest,
)
from pdmt5.dataframe import Mt5DataClient  # noqa: TC001

if TYPE_CHECKING:
    from fastapi.responses import Response

router = APIRouter(
    prefix="/api/v1",
    tags=["account"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/account",
    response_model=DataResponse,
    summary="Get account info",
    description="Get MetaTrader 5 account information",
)
async def get_account_info(
    mt5_client: Annotated[Mt5DataClient, Depends(get_mt5_client)],
    response_format: Annotated[ResponseFormat, Depends(get_response_format)],
    _request: Annotated[AccountInfoRequest, Depends()],
) -> DataResponse | Response:
    """Get account information.

    Returns:
        DataResponse for JSON requests, or a Parquet response.
    """
    dataframe = await run_in_threadpool(mt5_client.account_info_as_df)

    if response_format == ResponseFormat.PARQUET:
        return format_dataframe_to_parquet(dataframe)

    return format_dataframe_to_json(dataframe)


@router.get(
    "/terminal",
    response_model=DataResponse,
    summary="Get terminal info",
    description="Get MetaTrader 5 terminal information",
)
async def get_terminal_info(
    mt5_client: Annotated[Mt5DataClient, Depends(get_mt5_client)],
    response_format: Annotated[ResponseFormat, Depends(get_response_format)],
    _request: Annotated[TerminalInfoRequest, Depends()],
) -> DataResponse | Response:
    """Get terminal information.

    Returns:
        DataResponse for JSON requests, or a Parquet response.
    """
    dataframe = await run_in_threadpool(mt5_client.terminal_info_as_df)

    if response_format == ResponseFormat.PARQUET:
        return format_dataframe_to_parquet(dataframe)

    return format_dataframe_to_json(dataframe)
