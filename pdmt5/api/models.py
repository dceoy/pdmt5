"""Pydantic models for API request validation and response serialization."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ResponseFormat(StrEnum):
    """Response format enumeration."""

    JSON = "json"
    PARQUET = "parquet"


class ErrorResponse(BaseModel):
    """RFC 7807 Problem Details error response model."""

    type: str = Field(
        description="Error type URI",
        examples=["/errors/validation-error"],
    )
    title: str = Field(
        description="Short error summary",
        examples=["Request Validation Failed"],
    )
    status: int = Field(
        description="HTTP status code",
        ge=400,
        le=599,
        examples=[400],
    )
    detail: str = Field(
        description="Detailed error explanation",
        examples=["count must be positive (got: -10)"],
    )
    instance: str | None = Field(
        default=None,
        description="Request URI that caused error",
        examples=["/api/v1/rates/from"],
    )


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(
        description="API health status",
        examples=["healthy"],
    )
    mt5_connected: bool = Field(
        description="MT5 terminal connection status",
        examples=[True],
    )
    mt5_version: str | None = Field(
        default=None,
        description="MT5 terminal version",
        examples=["5.0.4321"],
    )
    api_version: str = Field(
        description="API version",
        examples=["1.0.0"],
    )


class DataResponse(BaseModel):
    """Generic data response model for market data endpoints."""

    data: list[dict[str, Any]] | dict[str, Any] = Field(
        description="Response data (array for multiple records, object for single)",
    )
    count: int = Field(
        ge=0,
        description="Number of records returned",
        examples=[100],
    )
    format: ResponseFormat = Field(
        description="Response format used",
        examples=[ResponseFormat.JSON],
    )
