"""Tests for User model."""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User


def test_create_user(session):
    """Test creating a basic user."""
    user = User(email="user@example.com")
    session.add(user)
    session.commit()

    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.email == "user@example.com"
    assert isinstance(user.created, datetime)
    assert user.settings is None


def test_create_user_with_settings(session):
    """Test creating a user with settings."""
    settings_data = {"theme": "dark", "language": "en", "notifications": True}
    user = User(email="settings@example.com", settings=settings_data)
    session.add(user)
    session.commit()

    assert user.settings == settings_data
    assert user.settings["theme"] == "dark"
    assert user.settings["notifications"] is True


def test_user_email_unique_constraint(session):
    """Test that user emails must be unique."""
    user1 = User(email="unique@example.com")
    session.add(user1)
    session.commit()

    # Try to create another user with same email
    user2 = User(email="unique@example.com")
    session.add(user2)

    with pytest.raises(IntegrityError):
        session.commit()


def test_user_email_required(session):
    """Test that email is required."""
    user = User()  # type: ignore
    session.add(user)

    with pytest.raises(IntegrityError):
        session.commit()


def test_user_repr(session):
    """Test User __repr__ method."""
    user = User(email="repr@example.com")
    session.add(user)
    session.commit()

    repr_str = repr(user)
    assert "User" in repr_str
    assert "repr@example.com" in repr_str
    assert str(user.id) in repr_str


def test_user_settings_json_storage(session):
    """Test that settings are stored as JSONB."""
    complex_settings = {
        "theme": "dark",
        "sidebar": {"collapsed": True, "width": 300},
        "recent_items": ["id1", "id2", "id3"],
        "count": 42,
    }
    user = User(email="json@example.com", settings=complex_settings)
    session.add(user)
    session.commit()

    # Refresh from database
    session.refresh(user)

    assert user.settings == complex_settings
    assert user.settings["sidebar"]["collapsed"] is True
    assert user.settings["recent_items"] == ["id1", "id2", "id3"]
    assert user.settings["count"] == 42


def test_user_created_timestamp_auto(session):
    """Test that created timestamp is automatically set."""
    user = User(email="timestamp@example.com")
    session.add(user)
    session.commit()

    assert user.created is not None
    # Verify timestamp is recent (within last minute)
    now = datetime.now(timezone.utc)
    assert abs((user.created - now).total_seconds()) < 60
