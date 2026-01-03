"""Health check and system information endpoints."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from pdmt5.api.auth import verify_api_key
from pdmt5.api.dependencies import (
    get_mt5_client,
    get_response_format,
    run_in_threadpool,
)
from pdmt5.api.formatters import format_dict_to_json, format_dict_to_parquet
from pdmt5.api.models import DataResponse, HealthResponse, ResponseFormat
from pdmt5.dataframe import Mt5DataClient  # noqa: TC001

if TYPE_CHECKING:
    from fastapi.responses import Response

router = APIRouter(prefix="/api/v1", tags=["health"])

# Package version
API_VERSION = "1.0.0"


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API and MT5 terminal connection status",
)
async def get_health() -> HealthResponse:
    """Check API health and MT5 terminal connectivity.

    This endpoint does NOT require authentication (public health check).

    Returns:
        HealthResponse: API and MT5 connection status.
    """
    mt5_connected = False
    mt5_version = None
    logger = logging.getLogger(__name__)

    try:
        client = get_mt5_client()
        mt5_connected = True

        # Get MT5 version
        version_dict = await run_in_threadpool(client.version_as_dict)
        if version_dict:
            mt5_version = f"{version_dict.get('version', 'unknown')}"
    except RuntimeError as e:
        # MT5 not connected - health check still succeeds
        logger.debug("MT5 not available for health check: %s", e)

    return HealthResponse(
        status="healthy" if mt5_connected else "unhealthy",
        mt5_connected=mt5_connected,
        mt5_version=mt5_version,
        api_version=API_VERSION,
    )


@router.get(
    "/version",
    response_model=DataResponse,
    summary="Get MT5 version",
    description="Get MetaTrader 5 terminal version information",
)
async def get_version(
    mt5_client: Annotated[Mt5DataClient, Depends(get_mt5_client)],
    api_key: Annotated[str, Depends(verify_api_key)],  # noqa: ARG001
    response_format: Annotated[ResponseFormat, Depends(get_response_format)],
) -> DataResponse | Response:
    """Get MT5 terminal version information.

    Args:
        mt5_client: MT5 data client dependency.
        api_key: API key for authentication (validated, unused in function).
        response_format: Negotiated response format.

    Returns:
        DataResponse for JSON requests, or a Parquet response.
    """
    version_dict = await run_in_threadpool(mt5_client.version_as_dict)

    if response_format == ResponseFormat.PARQUET:
        return format_dict_to_parquet(version_dict)

    return format_dict_to_json(version_dict)
