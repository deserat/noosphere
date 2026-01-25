"""
AuditLog model - Comprehensive audit trail for all system changes.

Preserves complete history with before/after snapshots.
item_id uses SET NULL on delete to preserve audit trail.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    """Audit trail for all system changes."""

    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique audit log entry identifier",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who performed the action",
    )

    item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Item affected (nullable, SET NULL on delete to preserve audit)",
    )

    action: Mapped[str] = mapped_column(
        nullable=False,
        comment="Action performed (create, update, delete, classify, etc.)",
    )

    before: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="State before change"
    )

    after: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="State after change"
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="When action occurred",
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(user_id={self.user_id}, action={self.action}, timestamp={self.timestamp})>"
        )
