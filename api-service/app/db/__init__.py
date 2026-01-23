"""
Database module for Noosphere API.

Provides database connection management, session handling, and model base.

Usage:
    from app.db import get_db_session
    from app.models.user import User

    with get_db_session() as session:
        users = session.query(User).all()

Note: Base is not exported from this module to avoid circular imports.
Import Base directly from app.db.base instead:
    from app.db.base import Base
"""

from app.db.session import (
    SessionLocal,
    check_database_health,
    connect_with_retry,
    engine,
    get_db_session,
)

__all__ = [
    "SessionLocal",
    "check_database_health",
    "connect_with_retry",
    "engine",
    "get_db_session",
]
