"""FastAPI application instance and lifecycle management."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from .dependencies import shutdown_mt5_client
from .middleware import add_middleware
from .routers import health

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Manage application lifespan (startup and shutdown).

    Args:
        app: FastAPI application instance (unused but required by FastAPI).

    Yields:
        None
    """
    # Startup
    logger.info("Starting MT5 REST API...")

    # Note: MT5 client is initialized lazily on first request via dependency
    # This avoids blocking startup if MT5 is not available
    await asyncio.sleep(0)  # Make function truly async

    yield

    # Shutdown
    logger.info("Shutting down MT5 REST API...")
    shutdown_mt5_client()
    logger.info("MT5 connection closed")


# Create FastAPI application
app = FastAPI(
    title="MT5 REST API",
    description=(
        "REST API for MetaTrader 5 data access. "
        "Provides read-only access to market data, "
        "account information, and trading history via HTTP endpoints."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add middleware
add_middleware(app)

# Include routers
app.include_router(health.router)

logger.info("MT5 REST API initialized")
