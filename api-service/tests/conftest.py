"""Pytest configuration and fixtures."""

import os
import pytest
from datetime import timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import _import_models


# Import all models for metadata
_import_models()


@pytest.fixture(scope="session")
def database_url():
    """Get database URL from environment or use test database."""
    return os.getenv("TEST_DATABASE_URL", "postgresql://noosphere_user:dev_password@localhost:5432/noosphere_test")


@pytest.fixture(scope="session")
def engine(database_url):
    """Create test database engine."""
    _engine = create_engine(database_url)
    return _engine


@pytest.fixture(scope="session", autouse=True)
def setup_database(engine):
    """Ensure database tables exist (assumes migration has been run)."""
    # Tables should already exist from Alembic migrations
    # We don't create/drop them to avoid conflicts
    yield


@pytest.fixture
def session(engine):
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()

    # Create session bound to connection
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    # Rollback transaction and close connection
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def user(session):
    """Create a test user."""
    from app.models.user import User

    test_user = User(
        email="test@example.com",
        settings={"theme": "dark", "notifications": True},
    )
    session.add(test_user)
    session.commit()
    session.refresh(test_user)
    return test_user


@pytest.fixture
def item(session, user):
    """Create a test item."""
    from app.models.item import Item, ItemState

    test_item = Item(
        title="Test Item",
        file_path="/test/item.md",
        category="notes",
        subcategory="personal",
        tags=["test", "example"],
        state=ItemState.NOT_STARTED,
        user_id=user.id,
        no_ai=False,
    )
    session.add(test_item)
    session.commit()
    session.refresh(test_item)
    return test_item
