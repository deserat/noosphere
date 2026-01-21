"""Tests for TokenUsage model."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.models.token_usage import TokenUsage


def test_create_token_usage(session, user):
    """Test creating a token usage record."""
    usage = TokenUsage(
        user_id=user.id,
        operation="classification",
        model="gpt-4",
        input_tokens=100,
        output_tokens=50,
        cost_usd=Decimal("0.001500"),
    )
    session.add(usage)
    session.commit()

    assert usage.id is not None
    assert isinstance(usage.id, uuid.UUID)
    assert usage.operation == "classification"
    assert usage.model == "gpt-4"
    assert usage.input_tokens == 100
    assert usage.output_tokens == 50
    assert usage.cost_usd == Decimal("0.001500")
    assert usage.timestamp is not None


def test_token_usage_cost_precision(session, user):
    """Test that cost is stored with 6 decimal precision."""
    usage = TokenUsage(
        user_id=user.id,
        operation="embedding",
        model="text-embedding-ada-002",
        input_tokens=500,
        output_tokens=0,
        cost_usd=Decimal("0.000123"),
    )
    session.add(usage)
    session.commit()

    session.refresh(usage)
    assert usage.cost_usd == Decimal("0.000123")


def test_token_usage_timestamp_auto(session, user):
    """Test that timestamp is automatically set."""
    usage = TokenUsage(
        user_id=user.id,
        operation="chat",
        model="gpt-4-turbo",
        input_tokens=1000,
        output_tokens=500,
        cost_usd=Decimal("0.010000"),
    )
    session.add(usage)
    session.commit()

    assert usage.timestamp is not None
    # Verify timestamp is recent (within last minute)
    now = datetime.now(timezone.utc)
    assert abs((usage.timestamp - now).total_seconds()) < 60


def test_token_usage_cascade_delete(session, user):
    """Test that usage records are deleted when user is deleted."""
    usage = TokenUsage(
        user_id=user.id,
        operation="test",
        model="test-model",
        input_tokens=100,
        output_tokens=50,
        cost_usd=Decimal("0.001000"),
    )
    session.add(usage)
    session.commit()

    usage_id = usage.id

    # Delete user
    session.delete(user)
    session.commit()

    # Usage should be deleted
    deleted_usage = session.query(TokenUsage).filter(TokenUsage.id == usage_id).first()
    assert deleted_usage is None


def test_token_usage_repr(session, user):
    """Test TokenUsage __repr__ method."""
    usage = TokenUsage(
        user_id=user.id,
        operation="test",
        model="test-model",
        input_tokens=100,
        output_tokens=50,
        cost_usd=Decimal("0.001000"),
    )
    session.add(usage)
    session.commit()

    repr_str = repr(usage)
    assert "TokenUsage" in repr_str
    assert "test" in repr_str or "test-model" in repr_str
