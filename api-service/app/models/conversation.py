"""
Conversation model - AI conversation history with RRD pattern.

Implements Retain-Reduce-Discard pattern for progressive summarization:
- full_transcript: Complete conversation (retained temporarily)
- detailed_summary: Reduced form (medium-term retention)
- brief_summary: Minimal summary (long-term retention)
- key_outcomes: Permanent distilled insights

Allows graceful degradation of conversation history over time.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Conversation(Base):
    """AI conversation with progressive summarization (RRD pattern)."""

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique conversation identifier",
    )

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Item this conversation is about",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User in the conversation",
    )

    session_start: Mapped[datetime] = mapped_column(
        default=func.now(),
        nullable=False,
        index=True,
        comment="When conversation session started",
    )

    session_end: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="When conversation session ended"
    )

    # ========== RRD Pattern Fields ==========
    full_transcript: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Complete conversation transcript (Retain phase)"
    )

    detailed_summary: Mapped[Optional[str]] = mapped_column(
        nullable=True, comment="Detailed summary of conversation (Reduce phase)"
    )

    brief_summary: Mapped[Optional[str]] = mapped_column(
        nullable=True, comment="Brief summary for long-term retention (Reduce phase)"
    )

    key_outcomes: Mapped[Optional[str]] = mapped_column(
        nullable=True, comment="Permanent distilled insights (Retain permanently)"
    )

    # ========== Metadata ==========
    detail_level: Mapped[Optional[str]] = mapped_column(
        nullable=True, comment="Current retention level (full, detailed, brief)"
    )

    last_summarized: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="When last reduction/summarization occurred"
    )

    changes_made: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="What edits resulted from this conversation"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, item_id={self.item_id}, detail_level={self.detail_level})>"
