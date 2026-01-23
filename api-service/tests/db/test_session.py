"""Tests for database session module."""

import uuid
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import OperationalError

from app.db.session import (
    SessionLocal,
    check_database_health,
    connect_with_retry,
    engine,
    get_db_session,
)
from app.models.user import User


def test_engine_exists():
    """Test that engine is created."""
    assert engine is not None
    assert engine.pool.size() >= 0  # Pool is initialized


def test_session_factory():
    """Test that SessionLocal creates sessions."""
    session = SessionLocal()
    assert session is not None
    # Verify it's a valid session by checking bind
    assert session.bind is not None
    session.close()


def test_get_db_session_success(session):
    """Test context manager commits on success."""
    unique_email = f"test-{uuid.uuid4()}@example.com"

    with get_db_session() as db_session:
        user = User(email=unique_email)
        db_session.add(user)

    # Verify user was committed (in a new session)
    saved_user = session.query(User).filter(User.email == unique_email).first()
    assert saved_user is not None


def test_get_db_session_rollback():
    """Test context manager rolls back on exception."""
    with pytest.raises(ValueError):
        with get_db_session() as db_session:
            user = User(email="rollback@example.com")
            db_session.add(user)
            raise ValueError("Force rollback")

    # Verify user was NOT saved
    with get_db_session() as db_session:
        saved_user = (
            db_session.query(User).filter(User.email == "rollback@example.com").first()
        )
        assert saved_user is None


def test_get_db_session_always_closes():
    """Test that session is always closed."""
    # Mock the close method to verify it gets called
    with patch("app.db.session.SessionLocal") as mock_session_factory:
        mock_session = Mock()
        mock_session_factory.return_value = mock_session

        # Successful case - should call commit and close
        with get_db_session():
            pass

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

        # Reset mocks
        mock_session.reset_mock()

        # Error case - should call rollback and close
        with pytest.raises(ValueError):
            with get_db_session():
                raise ValueError("Test error")

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


def test_check_database_health_success():
    """Test health check returns True when DB is accessible."""
    result = check_database_health()
    assert result is True


def test_check_database_health_failure():
    """Test health check returns False when DB is inaccessible."""
    with patch("app.db.session.engine.connect") as mock_connect:
        mock_connect.side_effect = OperationalError("Connection failed", None, None)
        result = check_database_health()
        assert result is False


def test_connect_with_retry_success():
    """Test retry logic succeeds on first attempt."""
    # Should not raise
    connect_with_retry()


def test_connect_with_retry_eventual_success():
    """Test retry logic succeeds after initial failures."""
    attempt_count = 0

    def mock_execute(query):
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise OperationalError("Temporary failure", None, None)
        # Succeed on second attempt

    with patch("app.db.session.engine.connect") as mock_connect:
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.execute = mock_execute
        mock_connect.return_value = mock_conn

        connect_with_retry()
        assert attempt_count == 2  # Failed once, succeeded second time


def test_connect_with_retry_max_attempts():
    """Test retry logic fails after max attempts."""
    with patch("app.db.session.engine.connect") as mock_connect:
        mock_connect.side_effect = OperationalError("Persistent failure", None, None)

        with pytest.raises(Exception):
            connect_with_retry()
