"""Tests for API authentication."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_version_endpoint_requires_authentication(client: TestClient) -> None:
    """Test version endpoint requires API key."""
    # No API key header
    response = client.get("/api/v1/version")

    assert response.status_code == 401

    data = response.json()["detail"]
    assert data["type"] == "/errors/unauthorized"
    assert data["title"] == "Authentication Required"
    assert "Missing API key" in data["detail"]


def test_version_endpoint_rejects_invalid_api_key(client: TestClient) -> None:
    """Test version endpoint rejects invalid API key."""
    headers = {"X-API-Key": "wrong-key"}
    response = client.get("/api/v1/version", headers=headers)

    assert response.status_code == 401

    data = response.json()["detail"]
    assert data["type"] == "/errors/unauthorized"
    assert data["title"] == "Authentication Failed"
    assert "Invalid API key" in data["detail"]


def test_version_endpoint_accepts_valid_api_key(
    client: TestClient,
    api_headers: dict[str, str],
) -> None:
    """Test version endpoint accepts valid API key."""
    response = client.get("/api/v1/version", headers=api_headers)

    assert response.status_code == 200
