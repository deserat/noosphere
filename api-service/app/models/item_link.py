"""
ItemLink model - Graph relationships between items.

Enables knowledge graph features with typed, directed links.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ItemLink(Base):
    """Directed, typed relationship between two items."""

    __tablename__ = "item_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique link identifier",
    )

    from_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Source item in relationship",
    )

    to_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Target item in relationship",
    )

    link_type: Mapped[str] = mapped_column(
        nullable=False,
        comment="Relationship type (related, references, depends-on, etc.)",
    )

    why_related: Mapped[Optional[str]] = mapped_column(
        nullable=True, comment="Explanation of the relationship"
    )

    confidence: Mapped[Optional[float]] = mapped_column(
        nullable=True, comment="AI confidence in this relationship (0.0-1.0)"
    )

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="When link was created",
    )

    __table_args__ = (
        UniqueConstraint(
            "from_item_id", "to_item_id", "link_type", name="uq_item_link_from_to_type"
        ),
        CheckConstraint("from_item_id != to_item_id", name="ck_item_link_no_self_links"),
    )

    def __repr__(self) -> str:
        return f"<ItemLink(from={self.from_item_id}, to={self.to_item_id}, type={self.link_type})>"
