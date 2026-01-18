"""
SQLAlchemy Base and metadata.

All models should import Base from this module and inherit from it.
This allows Alembic autogenerate to discover all models.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Import all models here for Alembic autogenerate discovery
# Example (when models are created in EPIC-2-2):
# from app.models.item import Item
# from app.models.user import User
# etc.
