"""Integration tests for FastAPI application lifespan and setup."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


def test_app_creation():
    """Test FastAPI app can be created successfully."""
    from app.main import app

    assert app is not None
    assert app.title == "Noosphere API"
    assert app.version == "0.1.0"


@pytest.fixture
def client():
    """Create test client for integration tests."""
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


def test_root_endpoint(client):
    """Test root endpoint returns service information."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Noosphere API"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"
    assert "/api/" in data["api"]


def test_cors_middleware_configured():
    """Test CORS middleware is properly configured."""
    from app.main import app
    from fastapi.middleware.cors import CORSMiddleware

    # Check middleware is present
    middleware_types = [m.cls for m in app.user_middleware]
    assert CORSMiddleware in middleware_types


def test_health_router_registered(client):
    """Test health router is registered at /health."""
    # Mock dependencies to avoid actual health checks
    with patch("app.api.endpoints.health.check_database_health", return_value=True):
        with patch(
            "app.api.endpoints.health.get_scheduler_status", return_value="running"
        ):
            response = client.get("/health")
            assert response.status_code == 200


def test_items_router_registered(client):
    """Test items router is registered at /api/v1/items."""
    response = client.get("/api/v1/items/")

    assert response.status_code == 200
    assert response.json() == []


def test_lifespan_startup_success(reset_singleton):
    """Test lifespan startup sequence executes successfully."""
    # Mock all startup dependencies
    mock_config = MagicMock()
    mock_config.api = {"host": "127.0.0.1", "port": 8000, "cors_origins": []}
    mock_config.scheduler = {"enabled": True}

    with patch("app.main.load_config", return_value=mock_config):
        with patch("app.main.connect_with_retry"):
            with patch("app.main.start_scheduler"):
                with patch("app.main.stop_scheduler"):
                    # Create test client - this triggers lifespan
                    from app.main import app

                    with TestClient(app):
                        # If we get here, startup succeeded
                        pass


def test_lifespan_startup_database_failure(reset_singleton):
    """Test lifespan fails fast when database connection fails."""
    # Mock config
    mock_config = MagicMock()
    mock_config.api = {"host": "127.0.0.1", "port": 8000, "cors_origins": []}
    mock_config.scheduler = {"enabled": True}

    with patch("app.main.load_config", return_value=mock_config):
        with patch(
            "app.main.connect_with_retry", side_effect=Exception("Database error")
        ):
            # Verify startup raises exception
            from app.main import app

            with pytest.raises(Exception, match="Database error"):
                with TestClient(app):
                    pass


def test_lifespan_startup_scheduler_failure(reset_singleton):
    """Test lifespan fails fast when scheduler fails to start."""
    # Mock config
    mock_config = MagicMock()
    mock_config.api = {"host": "127.0.0.1", "port": 8000, "cors_origins": []}
    mock_config.scheduler = {"enabled": True}

    with patch("app.main.load_config", return_value=mock_config):
        with patch("app.main.connect_with_retry"):
            with patch(
                "app.main.start_scheduler", side_effect=RuntimeError("Scheduler error")
            ):
                # Verify startup raises exception
                from app.main import app

                with pytest.raises(RuntimeError, match="Scheduler error"):
                    with TestClient(app):
                        pass


def test_lifespan_scheduler_disabled(reset_singleton):
    """Test lifespan skips scheduler when disabled in config."""
    # Mock config with scheduler disabled
    mock_config = MagicMock()
    mock_config.api = {"host": "127.0.0.1", "port": 8000, "cors_origins": []}
    mock_config.scheduler = {"enabled": False}

    with patch("app.main.load_config", return_value=mock_config):
        with patch("app.main.connect_with_retry"):
            with patch("app.main.start_scheduler") as mock_start:
                with patch("app.main.stop_scheduler"):
                    # Create test client
                    from app.main import app

                    with TestClient(app):
                        # Verify scheduler was not started
                        mock_start.assert_not_called()


def test_lifespan_shutdown(reset_singleton):
    """Test lifespan shutdown sequence executes successfully."""
    # Mock all dependencies
    mock_config = MagicMock()
    mock_config.api = {"host": "127.0.0.1", "port": 8000, "cors_origins": []}
    mock_config.scheduler = {"enabled": True}

    with patch("app.main.load_config", return_value=mock_config):
        with patch("app.main.connect_with_retry"):
            with patch("app.main.start_scheduler"):
                with patch("app.main.stop_scheduler") as mock_stop:
                    # Create and close test client - this triggers shutdown
                    from app.main import app

                    with TestClient(app):
                        pass  # Client context exit triggers shutdown

                    # Verify shutdown was called
                    mock_stop.assert_called_once()
