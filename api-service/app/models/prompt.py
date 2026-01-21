"""
Prompt model - AI prompt template management.

Stores versioned prompt templates with model configuration.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Prompt(Base):
    """AI prompt template with versioning support."""

    __tablename__ = "prompts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique prompt identifier",
    )

    name: Mapped[str] = mapped_column(
        nullable=False, comment="Prompt name (e.g., 'classify_item')"
    )

    version: Mapped[str] = mapped_column(
        nullable=False, comment="Prompt version (e.g., 'v1.0', 'v2.0')"
    )

    content: Mapped[str] = mapped_column(
        nullable=False, comment="Prompt template content"
    )

    model_config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="AI model configuration (temperature, max_tokens, etc.)",
    )

    active: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Whether this prompt version is active"
    )

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="Prompt creation timestamp",
    )

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_prompt_name_version"),
    )

    def __repr__(self) -> str:
        return (
            f"<Prompt(name={self.name}, version={self.version}, active={self.active})>"
        )
