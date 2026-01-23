"""
Item model - Core entity representing knowledge items in the vault.

Most complex model with:
- pgvector embedding for AI similarity search
- PostgreSQL array for tags
- Full-text search via tsvector (auto-populated by trigger)
- Multi-tenant support
- Comprehensive metadata and state management
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# OpenAI text-embedding-ada-002 dimension
EMBEDDING_DIMENSION = 1536


class ItemState(str, PyEnum):
    """Item workflow states."""

    UNCATEGORIZED = "uncategorized"
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Item(Base):
    """
    Core knowledge item with AI embeddings and full-text search.

    Supports:
    - Vector similarity search (pgvector)
    - Full-text search (tsvector with auto-populate trigger)
    - Multi-tenant architecture
    - AI classification and confidence scoring
    - Surfacing/scheduling metadata
    """

    __tablename__ = "items"

    # ========== Identity Fields ==========
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique item identifier",
    )

    title: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="Item title"
    )

    file_path: Mapped[str] = mapped_column(
        unique=True, nullable=False, comment="Vault file path (unique)"
    )

    # ========== Classification Fields ==========
    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        index=True,
        nullable=True,
        comment="Primary category (ideas, tasks, notes, resources, journal)",
    )

    subcategory: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Secondary classification"
    )

    tags: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String), nullable=True, comment="Tags for categorization (GIN indexed)"
    )

    # ========== State Management ==========
    state: Mapped[ItemState] = mapped_column(
        Enum(ItemState, name="item_state"),
        nullable=False,
        default=ItemState.UNCATEGORIZED,
        index=True,
        comment="Current workflow state",
    )

    # ========== Timestamp Fields ==========
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="Creation timestamp",
    )

    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last modification timestamp",
    )

    last_worked: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time item was actively worked on",
    )

    categorized_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When item was last categorized",
    )

    # ========== Surfacing Fields ==========
    next_surface: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=True,
        comment="When to surface this item next",
    )

    cadence: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="Surfacing cadence (daily, weekly, monthly)"
    )

    # ========== AI Fields ==========
    confidence: Mapped[Optional[float]] = mapped_column(
        nullable=True, comment="AI classification confidence (0.0-1.0)"
    )

    embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(EMBEDDING_DIMENSION),
        nullable=True,
        comment=f"Vector embedding for similarity search ({EMBEDDING_DIMENSION} dimensions)",
    )

    embedding_updated: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When embedding was last generated",
    )

    # ========== Sync Fields ==========
    content_hash: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="Content hash for change detection"
    )

    no_ai: Mapped[bool] = mapped_column(
        default=False, nullable=False, comment="Opt-out of AI processing"
    )

    # ========== Multi-tenant ==========
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Owner user (multi-tenant)",
    )

    # ========== Full-text Search ==========
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        nullable=True,
        comment="Full-text search vector (auto-populated by trigger)",
    )

    # ========== Constraints ==========
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1", name="ck_item_confidence_range"
        ),
        # GIN index for array operations on tags
        Index("idx_items_tags", "tags", postgresql_using="gin"),
        # GIN index for full-text search
        Index("idx_items_search_vector", "search_vector", postgresql_using="gin"),
        # Note: Vector index (ivfflat/hnsw) will be added in a later migration
        # after data exists, as these indexes require tuning parameters and data
        # for optimal configuration. B-tree indexes don't work for large vectors.
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, title={self.title[:30]}, state={self.state})>"
