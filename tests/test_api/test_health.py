"""Tests for health check endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_health_endpoint_returns_healthy_status(client: TestClient) -> None:
    """Test health endpoint returns healthy status when MT5 is connected."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["mt5_connected"] is True
    assert data["mt5_version"] == "5.0.4321"
    assert data["api_version"] == "1.0.0"


def test_health_endpoint_no_authentication_required(client: TestClient) -> None:
    """Test health endpoint works without authentication."""
    # No X-API-Key header
    response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_version_endpoint_returns_mt5_version(
    client: TestClient,
    api_headers: dict[str, str],
) -> None:
    """Test version endpoint returns MT5 version info."""
    response = client.get("/api/v1/version", headers=api_headers)

    assert response.status_code == 200

    data = response.json()
    assert data["version"] == "5.0.4321"
    assert data["build"] == 4321
    assert "release_date" in data
