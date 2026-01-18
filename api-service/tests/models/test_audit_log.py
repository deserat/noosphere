"""Tests for AuditLog model."""

import uuid
from datetime import datetime

from app.models.audit_log import AuditLog


def test_create_audit_log(session, user, item):
    """Test creating an audit log entry."""
    log = AuditLog(
        user_id=user.id,
        item_id=item.id,
        action="create",
        before=None,
        after={"title": "New Item", "state": "uncategorized"},
    )
    session.add(log)
    session.commit()

    assert log.id is not None
    assert isinstance(log.id, uuid.UUID)
    assert log.user_id == user.id
    assert log.item_id == item.id
    assert log.action == "create"
    assert log.before is None
    assert log.after["title"] == "New Item"


def test_audit_log_update_action(session, user, item):
    """Test audit log for update action."""
    log = AuditLog(
        user_id=user.id,
        item_id=item.id,
        action="update",
        before={"state": "not-started", "category": None},
        after={"state": "in-progress", "category": "tasks"},
    )
    session.add(log)
    session.commit()

    assert log.action == "update"
    assert log.before["state"] == "not-started"
    assert log.after["state"] == "in-progress"
    assert log.after["category"] == "tasks"


def test_audit_log_timestamp_auto(session, user, item):
    """Test that timestamp is automatically set."""
    log = AuditLog(user_id=user.id, item_id=item.id, action="classify")
    session.add(log)
    session.commit()

    assert log.timestamp is not None
    # Verify timestamp is recent (within last hour)
    now = datetime.now()
    assert abs((log.timestamp - now).total_seconds()) < 3600


def test_audit_log_nullable_item(session, user):
    """Test that item_id can be null (for deleted items)."""
    log = AuditLog(
        user_id=user.id,
        item_id=None,
        action="system_action",
        after={"result": "success"},
    )
    session.add(log)
    session.commit()

    assert log.item_id is None


def test_audit_log_set_null_on_item_delete(session, user, item):
    """Test that item_id is set to NULL when item is deleted."""
    log = AuditLog(
        user_id=user.id,
        item_id=item.id,
        action="update",
        before={"state": "not-started"},
        after={"state": "in-progress"},
    )
    session.add(log)
    session.commit()

    log_id = log.id

    # Delete item
    session.delete(item)
    session.commit()

    # Log should still exist but item_id should be NULL
    preserved_log = session.query(AuditLog).filter(AuditLog.id == log_id).first()
    assert preserved_log is not None
    assert preserved_log.item_id is None
    assert preserved_log.action == "update"


def test_audit_log_cascade_delete_user(session, user, item):
    """Test that logs are deleted when user is deleted."""
    log = AuditLog(user_id=user.id, item_id=item.id, action="test")
    session.add(log)
    session.commit()

    log_id = log.id

    # Delete user
    session.delete(user)
    session.commit()

    # Log should be deleted
    deleted_log = session.query(AuditLog).filter(AuditLog.id == log_id).first()
    assert deleted_log is None


def test_audit_log_complex_state_changes(session, user, item):
    """Test audit log with complex state changes."""
    before_state = {
        "title": "Old Title",
        "category": "notes",
        "tags": ["old", "tag"],
        "confidence": 0.5,
    }
    after_state = {
        "title": "New Title",
        "category": "tasks",
        "tags": ["new", "tag", "extra"],
        "confidence": 0.95,
    }

    log = AuditLog(
        user_id=user.id,
        item_id=item.id,
        action="ai_classify",
        before=before_state,
        after=after_state,
    )
    session.add(log)
    session.commit()

    assert log.before["confidence"] == 0.5
    assert log.after["confidence"] == 0.95
    assert len(log.after["tags"]) == 3


def test_audit_log_repr(session, user, item):
    """Test AuditLog __repr__ method."""
    log = AuditLog(user_id=user.id, item_id=item.id, action="test_action")
    session.add(log)
    session.commit()

    repr_str = repr(log)
    assert "AuditLog" in repr_str
    assert "test_action" in repr_str
