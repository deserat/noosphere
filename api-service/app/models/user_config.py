"""
UserConfig model - Key-value storage for user-specific configuration.

Uses composite primary key (user_id, key) for flexible settings storage.
"""
import uuid
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserConfig(Base):
    """User-specific configuration with composite primary key."""

    __tablename__ = "user_config"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Reference to user (composite PK part 1)",
    )

    key: Mapped[str] = mapped_column(
        primary_key=True, comment="Configuration key (composite PK part 2)"
    )

    value: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Configuration value (JSONB)"
    )

    def __repr__(self) -> str:
        return f"<UserConfig(user_id={self.user_id}, key={self.key})>"
