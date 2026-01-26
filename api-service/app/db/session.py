"""
Database session management module.

Provides connection pooling, session factory, context manager,
health checks, and retry logic for database operations.
"""

import logging
import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Ensures proper transaction handling:
    - Commits on success
    - Rolls back on exception
    - Always closes session

    Usage:
        with get_db_session() as session:
            user = session.query(User).first()
            # session commits automatically on exit

    Yields:
        Session: SQLAlchemy session object
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database_health() -> bool:
    """
    Check if database is accessible.

    Returns:
        True if database responds to simple query, False otherwise.

    Usage:
        if check_database_health():
            print("Database is healthy")
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except OperationalError as e:
        logger.warning(f"Database health check failed: {e}")
        return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def connect_with_retry() -> None:
    """
    Connect to database with exponential backoff retry.

    Retries up to 3 times with exponential backoff:
    - Attempt 1: Immediate
    - Attempt 2: Wait 1 second (min threshold)
    - Attempt 3: Wait 2 seconds

    Raises:
        Exception: If all retry attempts fail

    Usage:
        connect_with_retry()  # Ensures connection is established
    """
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
