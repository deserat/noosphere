"""Unit tests for health check endpoints."""

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


def test_health_endpoint_all_healthy(client):
    """Test /health returns 200 when all components are healthy."""
    with patch("app.api.endpoints.health.check_database_health", return_value=True):
        with patch(
            "app.api.endpoints.health.get_scheduler_status", return_value="running"
        ):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] is True
            assert data["scheduler"] == "running"
            assert data["version"] == "0.1.0"


def test_health_endpoint_database_unhealthy(client):
    """Test /health returns degraded status when database is down."""
    with patch("app.api.endpoints.health.check_database_health", return_value=False):
        with patch(
            "app.api.endpoints.health.get_scheduler_status", return_value="running"
        ):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["database"] is False
            assert data["scheduler"] == "running"


def test_health_endpoint_scheduler_not_running(client):
    """Test /health returns degraded status when scheduler is not running."""
    with patch("app.api.endpoints.health.check_database_health", return_value=True):
        with patch(
            "app.api.endpoints.health.get_scheduler_status", return_value="stopped"
        ):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["database"] is True
            assert data["scheduler"] == "stopped"


def test_health_endpoint_all_unhealthy(client):
    """Test /health returns degraded when all components are unhealthy."""
    with patch("app.api.endpoints.health.check_database_health", return_value=False):
        with patch(
            "app.api.endpoints.health.get_scheduler_status", return_value="stopped"
        ):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["database"] is False
            assert data["scheduler"] == "stopped"


def test_ready_endpoint_when_ready(client):
    """Test /health/ready returns 200 when service is ready."""
    with patch("app.api.endpoints.health.check_database_health", return_value=True):
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True


def test_ready_endpoint_when_not_ready(client):
    """Test /health/ready returns 200 with ready=false when database is down."""
    with patch("app.api.endpoints.health.check_database_health", return_value=False):
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is False


def test_live_endpoint_always_alive(client):
    """Test /health/live always returns 200 with alive=true."""
    response = client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True


def test_live_endpoint_no_dependencies(client):
    """Test /health/live doesn't check any dependencies."""
    # Verify it works even if database/scheduler checks would fail
    with patch(
        "app.api.endpoints.health.check_database_health",
        side_effect=Exception("Database error"),
    ):
        with patch(
            "app.api.endpoints.health.get_scheduler_status",
            side_effect=Exception("Scheduler error"),
        ):
            response = client.get("/health/live")

            # Should still return 200 - liveness doesn't check dependencies
            assert response.status_code == 200
            data = response.json()
            assert data["alive"] is True
