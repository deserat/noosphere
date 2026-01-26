"""Unit tests for placeholder items endpoints."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client for each test."""
    # Mock config and lifespan dependencies
    mock_config = MagicMock()
    mock_config.api = {"host": "127.0.0.1", "port": 8000, "cors_origins": []}
    mock_config.scheduler = {"enabled": True}

    with patch("app.main.load_config", return_value=mock_config):
        with patch("app.main.connect_with_retry"):
            with patch("app.main.start_scheduler"):
                with patch("app.main.stop_scheduler"):
                    from app.main import app

                    with TestClient(app) as test_client:
                        yield test_client


def test_list_items_returns_empty_list(client):
    """Test GET /api/v1/items returns empty list."""
    response = client.get("/api/v1/items/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_item_returns_404(client):
    """Test GET /api/v1/items/{id} returns 404."""
    response = client.get("/api/v1/items/123")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item not found"


def test_get_item_with_uuid_returns_404(client):
    """Test GET /api/v1/items/{id} returns 404 for UUID."""
    item_id = "550e8400-e29b-41d4-a716-446655440000"
    response = client.get(f"/api/v1/items/{item_id}")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item not found"


def test_create_item_returns_501(client):
    """Test POST /api/v1/items returns 501 Not Implemented."""
    response = client.post("/api/v1/items/", json={"title": "Test Item"})

    assert response.status_code == 501
    data = response.json()
    assert data["detail"] == "Not implemented yet"


def test_create_item_without_body_returns_501(client):
    """Test POST /api/v1/items returns 501 even without request body."""
    response = client.post("/api/v1/items/")

    assert response.status_code == 501
    data = response.json()
    assert data["detail"] == "Not implemented yet"


def test_update_item_returns_501(client):
    """Test PUT /api/v1/items/{id} returns 501 Not Implemented."""
    response = client.put("/api/v1/items/123", json={"title": "Updated"})

    assert response.status_code == 501
    data = response.json()
    assert data["detail"] == "Not implemented yet"


def test_update_item_without_body_returns_501(client):
    """Test PUT /api/v1/items/{id} returns 501 even without request body."""
    response = client.put("/api/v1/items/123")

    assert response.status_code == 501
    data = response.json()
    assert data["detail"] == "Not implemented yet"


def test_delete_item_returns_501(client):
    """Test DELETE /api/v1/items/{id} returns 501 Not Implemented."""
    response = client.delete("/api/v1/items/123")

    assert response.status_code == 501
    data = response.json()
    assert data["detail"] == "Not implemented yet"


def test_delete_item_with_uuid_returns_501(client):
    """Test DELETE /api/v1/items/{id} returns 501 for UUID."""
    item_id = "550e8400-e29b-41d4-a716-446655440000"
    response = client.delete(f"/api/v1/items/{item_id}")

    assert response.status_code == 501
    data = response.json()
    assert data["detail"] == "Not implemented yet"
