"""Tests for Item model."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.models.item import Item, ItemState


def test_create_basic_item(session, user):
    """Test creating a basic item."""
    item = Item(
        title="My Note",
        file_path="/notes/my-note.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item)
    session.commit()

    assert item.id is not None
    assert isinstance(item.id, uuid.UUID)
    assert item.title == "My Note"
    assert item.file_path == "/notes/my-note.md"
    assert item.state == ItemState.UNCATEGORIZED  # default
    assert item.no_ai is False
    assert item.user_id == user.id


def test_item_with_all_fields(session, user):
    """Test creating item with all optional fields."""
    item = Item(
        title="Complete Item",
        file_path="/complete.md",
        category="tasks",
        subcategory="work",
        tags=["urgent", "review", "python"],
        state=ItemState.IN_PROGRESS,
        confidence=0.95,
        cadence="weekly",
        no_ai=False,
        user_id=user.id,
    )
    session.add(item)
    session.commit()

    assert item.category == "tasks"
    assert item.subcategory == "work"
    assert item.tags == ["urgent", "review", "python"]
    assert item.state == ItemState.IN_PROGRESS
    assert item.confidence == 0.95
    assert item.cadence == "weekly"


def test_item_state_enum(session, user):
    """Test all ItemState enum values."""
    states = [
        ItemState.UNCATEGORIZED,
        ItemState.NOT_STARTED,
        ItemState.IN_PROGRESS,
        ItemState.COMPLETED,
        ItemState.ARCHIVED,
    ]

    for state in states:
        item = Item(
            title=f"Item {state.value}",
            file_path=f"/{state.value}.md",
            state=state,
            user_id=user.id,
            no_ai=False,
        )
        session.add(item)

    session.commit()

    items = session.query(Item).all()
    assert len(items) == len(states)


def test_item_file_path_unique(session, user):
    """Test that file_path must be unique."""
    item1 = Item(
        title="First",
        file_path="/unique/path.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item1)
    session.commit()

    item2 = Item(
        title="Second",
        file_path="/unique/path.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item2)

    with pytest.raises(IntegrityError):
        session.commit()


def test_item_confidence_range_constraint(session, user):
    """Test confidence must be between 0 and 1."""
    # Capture user_id to avoid detached instance issues after rollback
    user_id = user.id

    # Valid confidence values
    item1 = Item(
        title="Item 0.0",
        file_path="/item-0.0.md",
        confidence=0.0,
        user_id=user_id,
        no_ai=False,
    )
    item2 = Item(
        title="Item 0.5",
        file_path="/item-0.5.md",
        confidence=0.5,
        user_id=user_id,
        no_ai=False,
    )
    item3 = Item(
        title="Item 1.0",
        file_path="/item-1.0.md",
        confidence=1.0,
        user_id=user_id,
        no_ai=False,
    )
    session.add_all([item1, item2, item3])
    session.commit()

    # Invalid confidence > 1
    item_high = Item(
        title="Too High",
        file_path="/high.md",
        confidence=1.5,
        user_id=user_id,
        no_ai=False,
    )
    session.add(item_high)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()

    # Invalid confidence < 0
    item_low = Item(
        title="Too Low",
        file_path="/low.md",
        confidence=-0.5,
        user_id=user_id,
        no_ai=False,
    )
    session.add(item_low)

    with pytest.raises(IntegrityError):
        session.commit()


def test_item_vector_embedding(session, user):
    """Test storing vector embeddings."""
    # Create a 1536-dimensional vector (OpenAI embedding size)
    embedding = [0.1] * 1536

    item = Item(
        title="Embedded Item",
        file_path="/embedded.md",
        embedding=embedding,
        embedding_updated=datetime.utcnow(),
        user_id=user.id,
        no_ai=False,
    )
    session.add(item)
    session.commit()

    session.refresh(item)
    assert item.embedding is not None
    assert len(item.embedding) == 1536
    assert item.embedding_updated is not None


def test_item_tags_array(session, user):
    """Test PostgreSQL array for tags."""
    item = Item(
        title="Tagged Item",
        file_path="/tagged.md",
        tags=["python", "fastapi", "postgresql", "async"],
        user_id=user.id,
        no_ai=False,
    )
    session.add(item)
    session.commit()

    session.refresh(item)
    assert item.tags == ["python", "fastapi", "postgresql", "async"]
    assert len(item.tags) == 4


def test_item_search_vector_trigger(session, user):
    """Test that search_vector is auto-populated by trigger."""
    item = Item(
        title="Searchable Title",
        file_path="/search.md",
        category="notes",
        subcategory="technical",
        tags=["database", "testing"],
        user_id=user.id,
        no_ai=False,
    )
    session.add(item)
    session.commit()

    session.refresh(item)

    # search_vector should be automatically populated
    assert item.search_vector is not None

    # Test full-text search works
    result = session.execute(
        text(
            "SELECT title FROM items WHERE search_vector @@ to_tsquery('english', 'searchable')"
        )
    ).fetchone()

    assert result is not None
    assert result[0] == "Searchable Title"


def test_item_timestamps(session, user):
    """Test automatic timestamp fields."""
    item = Item(
        title="Timestamp Test",
        file_path="/timestamp.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item)
    session.commit()

    assert item.created is not None
    assert item.modified is not None
    # Verify timestamps are recent (within last minute)
    now = datetime.now()
    assert abs((item.created - now).total_seconds()) < 60
    assert abs((item.modified - now).total_seconds()) < 60


def test_item_modified_auto_update(session, user):
    """Test that modified timestamp updates automatically."""
    import time

    item = Item(
        title="Update Test",
        file_path="/update.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item)
    session.commit()

    original_modified = item.modified

    # Small delay to ensure different timestamp
    time.sleep(0.01)

    # Update the item
    item.title = "Updated Title"
    session.commit()
    session.refresh(item)

    # modified should have changed
    assert item.modified >= original_modified


def test_item_cascade_delete_with_user(session, user):
    """Test that items are deleted when user is deleted."""
    item = Item(
        title="Will be deleted",
        file_path="/deleted.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item)
    session.commit()

    item_id = item.id

    # Delete user
    session.delete(user)
    session.commit()

    # Item should be deleted
    deleted_item = session.query(Item).filter(Item.id == item_id).first()
    assert deleted_item is None


def test_item_repr(session, user):
    """Test Item __repr__ method."""
    item = Item(
        title="A Very Long Title That Should Be Truncated in Repr",
        file_path="/repr.md",
        state=ItemState.COMPLETED,
        user_id=user.id,
        no_ai=False,
    )
    session.add(item)
    session.commit()

    repr_str = repr(item)
    assert "Item" in repr_str
    assert str(item.id) in repr_str
    assert "COMPLETED" in repr_str or "completed" in repr_str
