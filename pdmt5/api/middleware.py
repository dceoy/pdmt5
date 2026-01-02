"""Error handling, logging, and CORS middleware."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware

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
        "Request: %s %s from %s",
        request.method,
        request.url.path,
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


def add_middleware(app: FastAPI) -> None:
    """Add all middleware to the FastAPI application.

    Args:
        app: FastAPI application instance.
    """
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.middleware("http")(error_handler_middleware)
    app.middleware("http")(logging_middleware)
