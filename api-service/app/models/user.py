"""
User model - Base entity for multi-tenancy.

Stores user accounts with email authentication and JSONB settings.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """User account model for multi-tenant system."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique user identifier",
    )

    email: Mapped[str] = mapped_column(
        unique=True, index=True, nullable=False, comment="User email address (unique)"
    )

    created: Mapped[datetime] = mapped_column(
        default=func.now(), nullable=False, comment="Account creation timestamp"
    )

    settings: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="User preferences and settings (JSONB)"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
