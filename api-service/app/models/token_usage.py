"""
TokenUsage model - Track AI API token consumption and costs.

Provides usage analytics and cost tracking for AI operations.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TokenUsage(Base):
    """AI API token usage and cost tracking."""

    __tablename__ = "token_usage"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique usage record identifier",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who incurred the usage",
    )

    operation: Mapped[str] = mapped_column(
        nullable=False, comment="Operation type (classification, embedding, chat, etc.)"
    )

    model: Mapped[str] = mapped_column(
        nullable=False, comment="AI model used (gpt-4, text-embedding-ada-002, etc.)"
    )

    input_tokens: Mapped[int] = mapped_column(
        nullable=False, comment="Number of input tokens consumed"
    )

    output_tokens: Mapped[int] = mapped_column(
        nullable=False, comment="Number of output tokens generated"
    )

    cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(10, 6),  # Up to $9999.999999 with 6 decimal precision
        nullable=False,
        comment="Cost in USD (precise to 6 decimals)",
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="When the operation occurred",
    )

    def __repr__(self) -> str:
        return f"<TokenUsage(user_id={self.user_id}, operation={self.operation}, model={self.model}, cost=${self.cost_usd:.4f})>"
