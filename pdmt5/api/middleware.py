"""Error handling, logging, and rate limiting middleware."""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from pdmt5.mt5 import Mt5RuntimeError

from .models import ErrorResponse

if TYPE_CHECKING:
    from fastapi import FastAPI
    from starlette.middleware.base import RequestResponseEndpoint
    from starlette.responses import Response

logger = logging.getLogger(__name__)


async def error_handler_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Handle errors and convert to RFC 7807 Problem Details responses.

    Args:
        request: FastAPI request object.
        call_next: Next middleware or endpoint handler.

    Returns:
        Response with error details in RFC 7807 format.
    """
    try:
        return await call_next(request)
    except Mt5RuntimeError as e:
        # MT5 terminal connection errors
        error = ErrorResponse(
            type="/errors/mt5-error",
            title="MT5 Terminal Error",
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
            instance=str(request.url),
        )
        logger.exception("MT5 error")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error.model_dump(),
        )
    except ValidationError as e:
        # Pydantic validation errors
        error = ErrorResponse(
            type="/errors/validation-error",
            title="Request Validation Failed",
            status=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            instance=str(request.url),
        )
        logger.warning("Validation error: %s", e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error.model_dump(),
        )
    except ValueError as e:
        # Value errors (invalid input)
        error = ErrorResponse(
            type="/errors/invalid-input",
            title="Invalid Input",
            status=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            instance=str(request.url),
        )
        logger.warning("Invalid input: %s", e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error.model_dump(),
        )
    except RuntimeError as e:
        # Runtime errors (MT5 not initialized, etc.)
        error = ErrorResponse(
            type="/errors/runtime-error",
            title="Runtime Error",
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
            instance=str(request.url),
        )
        logger.exception("Runtime error")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error.model_dump(),
        )
    except Exception as e:
        # Unexpected errors
        error = ErrorResponse(
            type="/errors/internal-error",
            title="Internal Server Error",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e!s}",
            instance=str(request.url),
        )
        logger.exception("Unexpected error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error.model_dump(),
        )


async def logging_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Log all requests and responses with timing information.

    Args:
        request: FastAPI request object.
        call_next: Next middleware or endpoint handler.

    Returns:
        Response from endpoint handler.
    """
    start_time = time.time()

    # Log request
    logger.info(
        "Request: %s %s params=%s from %s",
        request.method,
        request.url.path,
        dict(request.query_params),
        request.client.host if request.client else "unknown",
    )

    # Process request
    response = await call_next(request)

    # Log response with timing
    process_time = time.time() - start_time
    logger.info(
        "Response: %s %s -> %d (%.3fs)",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )

    # Add timing header
    response.headers["X-Process-Time"] = f"{process_time:.3f}"

    return response


def _build_default_rate_limit() -> str:
    """Build the default rate limit string from environment config.

    Returns:
        Default rate limit string in slowapi format.
    """
    raw_limit = os.getenv("API_RATE_LIMIT", "100")

    try:
        limit_value = max(1, int(raw_limit))
    except ValueError:
        limit_value = 100

    return f"{limit_value}/minute"


def add_middleware(app: FastAPI) -> None:
    """Add middleware and error handlers to the FastAPI application.

    Args:
        app: FastAPI application instance.
    """
    # Configure rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[_build_default_rate_limit()],
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # Add custom middleware
    app.middleware("http")(error_handler_middleware)
    app.middleware("http")(logging_middleware)


def _rate_limit_exceeded_handler(
    request: Request,  # noqa: ARG001
    exc: Exception,  # noqa: ARG001
) -> JSONResponse:
    """Handle rate limiting errors.

    Returns:
        JSON response describing the rate limit error.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "type": "/errors/rate-limit",
            "title": "Rate Limit Exceeded",
            "status": status.HTTP_429_TOO_MANY_REQUESTS,
            "detail": "Too many requests. Please slow down.",
            "instance": None,
        },
    )
