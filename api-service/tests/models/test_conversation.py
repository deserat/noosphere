"""Tests for Conversation model."""

import uuid
from datetime import datetime, timezone

from app.models.conversation import Conversation


def test_create_conversation(session, user, item):
    """Test creating a conversation."""
    conv = Conversation(
        item_id=item.id,
        user_id=user.id,
        full_transcript={"messages": [{"role": "user", "content": "Hello"}]},
    )
    session.add(conv)
    session.commit()

    assert conv.id is not None
    assert isinstance(conv.id, uuid.UUID)
    assert conv.item_id == item.id
    assert conv.user_id == user.id
    assert conv.full_transcript["messages"][0]["content"] == "Hello"


def test_conversation_rrd_fields(session, user, item):
    """Test Retain-Reduce-Discard pattern fields."""
    conv = Conversation(
        item_id=item.id,
        user_id=user.id,
        full_transcript={"messages": []},
        detailed_summary="Detailed summary of the conversation",
        brief_summary="Brief summary",
        key_outcomes="Main decisions and outcomes",
        detail_level="detailed",
    )
    session.add(conv)
    session.commit()

    assert conv.detailed_summary == "Detailed summary of the conversation"
    assert conv.brief_summary == "Brief summary"
    assert conv.key_outcomes == "Main decisions and outcomes"
    assert conv.detail_level == "detailed"


def test_conversation_session_timestamps(session, user, item):
    """Test session start and end timestamps."""
    start_time = datetime.now(timezone.utc)
    conv = Conversation(
        item_id=item.id,
        user_id=user.id,
        session_start=start_time,
    )
    session.add(conv)
    session.commit()

    assert conv.session_start == start_time
    assert conv.session_end is None

    # Update with end time
    end_time = datetime.now(timezone.utc)
    conv.session_end = end_time
    session.commit()

    assert conv.session_end == end_time


def test_conversation_changes_made(session, user, item):
    """Test storing changes made during conversation."""
    changes = {
        "files_modified": ["/notes/item.md"],
        "fields_updated": ["category", "tags"],
        "summary": "Categorized as task and added tags",
    }
    conv = Conversation(
        item_id=item.id,
        user_id=user.id,
        changes_made=changes,
    )
    session.add(conv)
    session.commit()

    assert conv.changes_made == changes
    assert conv.changes_made["files_modified"] == ["/notes/item.md"]


def test_conversation_cascade_delete_item(session, user, item):
    """Test that conversations are deleted when item is deleted."""
    conv = Conversation(item_id=item.id, user_id=user.id)
    session.add(conv)
    session.commit()

    conv_id = conv.id

    # Delete item
    session.delete(item)
    session.commit()

    # Conversation should be deleted
    deleted_conv = session.query(Conversation).filter(Conversation.id == conv_id).first()
    assert deleted_conv is None


def test_conversation_cascade_delete_user(session, user, item):
    """Test that conversations are deleted when user is deleted."""
    conv = Conversation(item_id=item.id, user_id=user.id)
    session.add(conv)
    session.commit()

    conv_id = conv.id

    # Delete user
    session.delete(user)
    session.commit()

    # Conversation should be deleted
    deleted_conv = session.query(Conversation).filter(Conversation.id == conv_id).first()
    assert deleted_conv is None


def test_conversation_repr(session, user, item):
    """Test Conversation __repr__ method."""
    conv = Conversation(item_id=item.id, user_id=user.id)
    session.add(conv)
    session.commit()

    repr_str = repr(conv)
    assert "Conversation" in repr_str
    assert str(conv.id) in repr_str
