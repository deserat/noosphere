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
# These imports ensure models are in Base.metadata for Alembic autogenerate
# NOTE: These are at module level to avoid circular imports during normal runtime.
# Alembic's env.py will import this module, triggering these imports.
#
# To avoid circular import errors when importing models directly, we do a late import:
def _import_models():
    """Import all models for Alembic discovery. Called by env.py."""
    from app.models.audit_log import AuditLog  # noqa: F401
    from app.models.conversation import Conversation  # noqa: F401
    from app.models.item import Item  # noqa: F401
    from app.models.item_link import ItemLink  # noqa: F401
    from app.models.prompt import Prompt  # noqa: F401
    from app.models.token_usage import TokenUsage  # noqa: F401
    from app.models.user import User  # noqa: F401
    from app.models.user_config import UserConfig  # noqa: F401
